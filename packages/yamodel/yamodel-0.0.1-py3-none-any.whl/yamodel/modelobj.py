
"""
Documentation at:
http://lngdays-dev080/external-api/Wiki/wiki/247/modelobjpy
"""

class modelobj:
    """ A generic expandable class for holding model objects. Typically supports an id and type attribute. """
    
    def __init__(self, dictionary=None):
        if dictionary:
            self.fill(dictionary)
            
    def fill(self, dictionary):
        """ Populates the modelobj with values from the dictionary. Dictionary properties
            or lists of dictionaries are deeply converted to modelobjs as well.  Property assignment is
            unique, and messages will be printed if an existing property is written to.
            """
        for kv in dictionary.items():
            v = kv[1]
            # lists of dictionaries are mapped to lists of modelobjs
            if isinstance(v, list):
                v = [modelobj(i) if isinstance(i, dict) else i for i in v]
            # inner dictionaries are also mapped to modelobjs
            elif isinstance(v, dict):
                v = modelobj(v)
            # help YAML out by making booleans from y/n
            elif v == 'y':
                v = True
            elif v == 'n':
                v = False

            # check on the current value for this attribute name
            currentvalue = getattr(self, kv[0], None)
            if currentvalue is not None and currentvalue != v:
                # if we already have a list in this property, merge new or updated
                # values into the existing modelobjs
                if isinstance(v, list):
                    for i in v:
                        ismodel = isinstance(i, modelobj)
                        found = next((f for f in currentvalue if f == i or (ismodel and f.id == i.id)), None)
                        if found:
                            if ismodel:
                                found.fill(i)
                        else:
                            currentvalue.append(i)
                    continue
                # yell about property collision
                if kv[0] != 'id' and kv[0] != 'type':
                    print('property collision ', self.type, kv[0], currentvalue, v)
                continue
            # set the attribute
            setattr(self, kv[0], v)

    def __iter__(self):
        """ List out non-private, non-callable attributes as name/value tuples. """
        for d in dir(self):
            if d.startswith('_'):
                continue
            v = getattr(self, d)
            if callable(v):
                continue
            yield (d, v)

    def items(self):
        """ Do a dictionary impression. """
        return self.__iter__()

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        """ Looks up attributes by name.  Missing attributes result in None and no exception. """
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        """ Sets attributes by name.  """
        setattr(self, key, value)
    
    def __repr__(self):
        """ Give model objects a usable text version. """
        s = ''
        for d in dir(self):
            if d.startswith('_'):
                continue
            v = getattr(self, d)
            if callable(v):
                continue
            s += '{0} = {1}; '.format(d, v)
        return s
