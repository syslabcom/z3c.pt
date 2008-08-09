import sys
import logging
import config

# check if we're able to coerce unicode to str
try:
    str(u'La Pe\xf1a')
    unicode_required_flag = False
except UnicodeEncodeError:
    unicode_required_flag = True
    log = logging.getLogger('z3c.pt')
    log.info("Default system encoding is set to '%s'; "
             "the template engine will perform better if "
             "an encoding that coerces gracefully to "
             "unicode is used ('utf-8' recommended)." % sys.getdefaultencoding())

s_counter = 0

def handler(key=None):
    def decorate(f):
        def g(node):
            if key is None:
                return f(node, None)
            return f(node, node.get(key))
        g.__ns__ = key
        return g
    return decorate

def attribute(ns, factory=None, default=None):
    def get(self):
        value = self.attrib.get(ns)
        if value is not None:
            if factory is None:
                return value
            f = factory(self.translator)
            return f(value)
        elif default is not None:
            return default
        
    return property(get)

class scope(list):
    def __init__(self, *args):
        global s_counter
        self.hash = s_counter
        s_counter += 1

    def __hash__(self):
        return self.hash

class repeatitem(object):
    def __init__(self, iterator, length):
        self.length = length
        self.iterator = iterator
        
    @property
    def index(self):
        try:
            length = len(self.iterator)
        except TypeError:
            length = self.iterator.__length_hint__()
        except:
            raise TypeError("Unable to determine length.")

        try:
            return self.length - length - 1
        except TypeError:
            return None
            
    @property
    def start(self):
        return self.index == 0

    @property
    def end(self):
        return self.index == self.length - 1

    def number(self):
        return self.index + 1

    def odd(self):
        return bool(self.index % 2)

    def even(self):
        return not self.odd()

class repeatdict(dict):
    def insert(self, key, iterable):
        length = len(iterable)
        iterator = iterable.__iter__()
        self[key] = (iterator, length)
        return iterator
        
    def __getitem__(self, key):
        value, length = dict.__getitem__(self, key)

        if not isinstance(value, repeatitem):
            value = repeatitem(value, length)
            self[key] = (value, length)
            
        return value

def xml_attr(name):
    return "{%s}%s" % (config.XML_NS, name)

def tal_attr(name):
    return "{%s}%s" % (config.TAL_NS, name)

def metal_attr(name):
    return "{%s}%s" % (config.METAL_NS, name)

def i18n_attr(name):
    return "{%s}%s" % (config.I18N_NS, name)

def py_attr(name):
    return "{%s}%s" % (config.PY_NS, name)
