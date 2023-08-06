from collections import defaultdict
import yaml
from yamodel.modelobj import modelobj
import copy


"""
Documentation is at:
http://lngdays-dev080/external-api/Wiki/wiki/245
"""

def toiter(item):
    """ Return a valid iterable when item is None, a string, a list, or some other value. """
    from collections import Iterable

    if item is None:
        return []
    if isinstance(item, str):
        return [item]
    if isinstance(item, Iterable):
        return item
    return [item]


def fmap(o, func, owner=None, index=None):
    if isinstance(o, list):
        for i, v in enumerate(o):
            fmap(v, func, o, i)
    elif isinstance(o, dict):
        for k, v in o.items():
            fmap(v, func, o, k)
    elif o is None:
        pass
    elif owner is not None and index is not None:
        owner[index] = func(o)


def check_const(m, consts):
    if consts:
        fmap(m, lambda v: consts.get(v, v) if isinstance(v, str) and len(v) > 0 and v[0] == '$' else v)
    return m


def load_yaml(filename, loadedfiles=None):
    """ Load a YAML model from a root file or pattern.
    Any files indicated by ModelImport models will also be loaded. """
    import glob
    import os.path
    # track a set of loaded files so that nothing is loaded a second time by import loops
    loaded = loadedfiles if loadedfiles else set()
    yamldocs = []
    constants = dict()
    for f in glob.glob(filename):
        if f not in loaded:
            loaded.add(f)
            for yamldoc in yaml.load_all(open(f, encoding='utf-8')):
                if not yamldoc:
                    continue
                for k, v in list(yamldoc.items()):
                    if k.startswith('$'):
                        constants[k] = v
                        del yamldoc[k]
                if len(yamldoc) == 0:
                    continue
                t = yamldoc['type']
                # expand any ModelImport models
                if t == 'ModelImport':
                    for importfile in yamldoc['files']:
                        relfile = os.path.join(os.path.dirname(f), importfile)
                        for importedmodel in load_yaml(relfile, loaded):
                            yamldocs.append(importedmodel)
                else:
                    yamldocs.append(yamldoc)

    if len(constants) > 0:
        constants['type'] = 'Constants'
        constants['id'] = 'Constants'
        yamldocs.append(constants)
    return yamldocs


def process_models(yamldocs):
    """ Convert a list of YAML documents into modelobjs and return the domain of models. """
    # the name map of TypeDef models
    typedefs = defaultdict(modelobj)
    # the name map of types to ID lookups, i.e. modeldefs['sometype']['someid'] == somemodelobj
    modeldefs = defaultdict(lambda: defaultdict(modelobj))
    # a flat list of all entities, used to track new model creation
    allmodels = []

    def getmodel(modeltype, modelid):
        """ Look up a model by type and ID, creating it if it doesn't exist yet. """
        e = modeldefs[modeltype][modelid]
        if not e['id'] and modelid:
            allmodels.append(e)
        e.type = modeltype
        e.id = modelid
        return e

    def fixup_mref(parentmodel, typedef, tdprop):
        """ Fulfill mrefs as specified in TypeDefs. """
        mref = typedef[tdprop]
        # remove "mref "
        mref = mref[5:]
        id = parentmodel[tdprop]
        if id:
            if isinstance(id, str):
                # supports mref fixup for reference by ID
                model = getmodel(mref, id)
                parentmodel[tdprop] = model
            else:
                # supports mref fixup for embedded entity
                model = getmodel(mref, id.id)
                model.fill(id)
                parentmodel[tdprop] = model
        else:
            parentmodel[tdprop] = None

    def fixup_mcol(entity, typedef, tdprop):
        """ Fulfill mcols as specified in TypeDefs. """
        mcol = typedef[tdprop]
        # remove "mcol "
        mcol = mcol[5:]
        col = entity[tdprop]
        if col:
            for i in range(len(col)):
                e = col[i]
                # if this is a list of strings, treat it like a list of model IDs
                if isinstance(e, str):
                    e = getmodel(mcol, entity.id + '.' + e)
                    e.name = col[i]
                if not e['id']:
                    e['id'] = mcol + str(len(allmodels))
                if not isinstance(e.id, str):
                    e.id = str(e.id)
                # collection-based models prepend their parent's ID
                if e.id.startswith(entity.id + '.'):
                    newid = e.id
                else:
                    newid = entity.id + '.' + e.id
                # get the model and fill in any properties
                model = getmodel(mcol, newid)
                model.fill(e)
                model.id = newid
                # set a few properties for politeness.  name is the original name, and parent is the owner's ID
                if not model['name']:
                    model.name = e.id
                if not model['parent']:
                    model.parent = entity.id
                # replace the item in the actual list
                col[i] = model
        else:
            entity[tdprop] = []

    def build_model_from_typedef(entity):
        """ Apply typedef properties to the model. """
        typedef = typedefs[entity.type]
        for tdprop, tdvalue in typedef:
            # skip id/type, fill mref/mcol, and copy defaults for anything else that's missing
            if tdprop == 'type' or tdprop == 'id':
                continue
            if str(tdvalue).startswith('mref '):
                fixup_mref(entity, typedef, tdprop)
            elif str(tdvalue).startswith('mcol '):
                fixup_mcol(entity, typedef, tdprop)
            else:
                currval = entity[tdprop]
                if currval is None:
                    entity[tdprop] = tdvalue

    def check_rules(modeldefs):
        """ Applies all of the defined rules to their appropriate model sets, writing failures to stderr. """
        import sys

        for r in modeldefs['Rule'].values():
            # "all" rules must be satisfied by all models of a given type
            for allrule in toiter(r.all):
                if r.target:
                    for m in modeldefs[r.target.id].values():
                        result = check_rule(allrule, m, modeldefs)
                        if not result:
                            sys.stderr.write('Rule failed: {0}\n All {1} {2}\n\n'.format(r.id, m.type, m.id))
                else:
                    if not check_rule(allrule, None, modeldefs):
                        sys.stderr.write('Rule failed: {0}\n\n'.format(r.id))
            # "any" rules must be satisfied by at least one model of a given type
            for anyrule in toiter(r.any):
                passed = False
                for m in modeldefs[r.target.id].values():
                    result = check_rule(anyrule, m, modeldefs)
                    if result:
                        passed = True
                        break
                if not passed:
                    sys.stderr.write('Rule failed: {0}\n Any {1}\n\n'.format(r.id, m.type))

    def check_rule(expr, m, modeldefs):
        """ Evaluate the rule expression against a model, which has its attributes imported to the local scope. """
        import sys
        envlocals = dict(m) if m else dict()
        envlocals['all_models'] = modeldefs
        envlocals['current_model'] = m
        try:
            if not '\n' in expr:
                return eval(expr, None, envlocals)
            else:
                statements = 'def ___run___():\n    ' + expr.replace('\n', '\n    ') + '\n__result = ___run___()'
                exec(statements, envlocals, envlocals)
                return envlocals['__result']
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            return None

    def build_model(m, consts=None):
        if not m['id']:
            m['id'] = m['type'] + str(len(allmodels))
        check_const(m, consts)
        model = getmodel(m['type'], m['id'])
        model.fill(m)
        return model

    def list_models(docs, include=None, exclude=None):
        for d in docs:
            ty = d['type']
            if include:
                if ty in include:
                    yield d
            elif exclude:
                if not ty in exclude:
                    yield d
            else:
                yield d

    def deep_update(root, updatetext):
        if isinstance(root, str):
            return updatetext(root)
        elif isinstance(root, dict) or isinstance(root, modelobj):
            for k, v in root.items():
                root[k] = deep_update(v, updatetext)
        elif isinstance(root, list):
            for i, subitem in enumerate(root):
                root[i] = deep_update(subitem, updatetext)
        return root

    for const in list_models(yamldocs, include=['Constants']):
        build_model(const)

    consts = modeldefs['Constants']
    if len(consts) > 1:
        raise Exception("Invalid constant definitions")
    consts = consts['Constants']

    for typedef in list_models(yamldocs, include=['TypeDef']):
        td = build_model(typedef, consts)
        typedefs[td.id] = td

    for template in list_models(yamldocs, include=['Template']):
        build_model(template, consts)

    for tempinst in list_models(yamldocs, include=['TemplateInstance']):
        inst = tempinst['template']
        template = modeldefs['Template'][inst] if isinstance(inst, str) else inst

        check_const(template, consts) # fmap(template, lambda v: consts.get(v, v))
        templateinput = tempinst['input'] if 'input' in tempinst else None
        if templateinput:
            for tempinput in templateinput:
                instance = copy.deepcopy(template['output'])
                for k, v in tempinput.items():
                    instance = deep_update(instance, lambda t: t.replace('('+k+')', v))
                yamldocs.append(instance)

    for m in list_models(yamldocs, exclude=['TypeDef', 'ModelImport', 'Template', 'TemplateInstance', 'Constants']):
        build_model(m, consts)

    # process the existential templates - adding values to all models of a given type
    for tempinst in list_models(yamldocs, include=['TemplateInstance']):
        inst = tempinst['template']
        template = modeldefs['Template'][inst] if isinstance(inst, str) else inst
        template = check_const(template, consts)
        templateinput = tempinst['input'] if 'input' in tempinst else None
        if not templateinput:
            for e in modeldefs[template['targettype']].values():
                instance = copy.deepcopy(template['output'])
                e.fill(instance)

    # apply TypeDefs to all models.  since this process can create new models, keep repeating until
    # all models have been created and processed.
    offset = 0
    while True:
        build_model_from_typedef(allmodels[offset])
        offset += 1
        if offset >= len(allmodels):
            break

    typedefs.default_factory = None
    modeldefs.default_factory = None
    for md in modeldefs.values():
        md.default_factory = None

    # run all rule checks against the model domain        
    check_rules(modeldefs)

    # return the domain
    return typedefs, modeldefs, allmodels


def build(filename):
    """ Builds YAML models from a starting file or pattern, and returns the resulting domain. """
    typedefs, modeldefs, allmodels = process_models(load_yaml(filename))
    domain = modelobj()
    domain.types = typedefs
    domain.typemap = modeldefs
    domain.models = allmodels
    for m in modeldefs.items():
        domain[m[0]] = [value for (key, value) in sorted(m[1].items())]
    return domain

