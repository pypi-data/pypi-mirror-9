from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import operator
import six
from itertools import chain

from jsonpath_rw import jsonpath
from jsonpath_rw.parser import parse as parse_jsonpath

from commcare_export.repeatable_iterator import RepeatableIterator

JSONPATH_CACHE = {}

class CannotBind(Exception): pass
class CannotReplace(Exception): pass
class CannotEmit(Exception): pass
class NotFound(Exception): pass

class Env(object):
    """
    An abstract model of an "environment" where data can be bound to
    names and later looked up. Not simply a dictionary as lookup in our
    case may support JsonPath, or may be a chaining of other
    environments, so the abstract interface will
    allow experimentation and customization.
    """

    #
    # Interface
    #
    def bind(self, name, value):
        """
        (key, ??) -> Env 

        Returns a new environment that is equivalent
        to the current except the provided key is
        bound to the value passed in. If the environment
        does not support such a binding, raises 
        CannotBind
        """
        raise NotImplementedError()

    def lookup(self, key):
        """
        key -> ??

        Note that the ?? may be None which may mean
        the value was unbound or may mean it was
        found and was None. This may need revisiting.
        This may also raise NotFound if it is the
        sort of environment that does that.
        """
        raise NotImplementedError()

    def replace(self, data):
        """
        data -> Env

        Completely replace the environment with new
        data (somewhat like "this"-based Map functions a la jQuery).
        Could be the same as creating a new empty env
        and binding "@" in JsonPath.

        May raise CannotReplace if this environment does
        not support the input replacement
        """
        raise NotImplementedError()

    # Minor impurity of the idea of a binding env:
    # also allow `Emit` to directly call into
    # the environment. It is up to the env
    # whether to store it, write it immediately,
    # or do something clever with iterators, etc.
    def emit_table(self, table_spec):
        raise NotImplementedError()

    def emitted_tables(self):
        raise NotImplementedError()
    
    #
    # Fluent interface to combinators
    #
    def __or__(self, other):
        return OrElse(self, other)

#
# Combinators
#

class OrElse(Env):
    """
    An environment that chains together a left environment
    and a right environment. Note that this differes from
    just a bunch of bindings, as the two envs might have
    entirely different mechanisms (for example a magic
    environment for special operators vs a JsonPathEnv
    that always returns a list and operates only on
    simple data)
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def bind(self, name, value):
        try:               return OrElse(self.left.bind(name, value), self.right)
        except CannotBind: return OrElse(self.left, self.right.bind(name, value))

    def lookup(self, name):
        try:             return self.left.lookup(name)
        except NotFound: return self.right.lookup(name)

    def replace(self, data):
        # A bit sketchy...
        try:                  return OrElse(self.left.replace(data), self.right)
        except CannotReplace: return OrElse(self.left, self.right.replace(data))

    def emit_table(self, table_spec):
        try:               return self.left.emit_table(table_spec)
        except CannotEmit: return self.right.emit_table(table_spec)

    def emitted_tables(self):
        return RepeatableIterator(lambda: chain(self.left.emitted_tables(), self.right.emitted_tables()))


#
# Concrete environment classes
# 

class DictEnv(Env):
    """
    A simple dictionary environment; more-or-less boring!
    """
    def __init__(self, d=None):
        self.d = d or {}

    def bind(self, name, value):
        return DictEnv(dict(self.d.items() + [(name, value)]))
        
    def lookup(self, name):
        try:             return self.d[name]
        except KeyError: raise NotFound()

    def replace(self, data):
        if isinstance(data, dict): return DictEnv(data)
        else:                      raise CannotReplace()

    def emit_table(self, table_spec):
        raise CannotEmit()

    def emitted_tables(self):
        return []
    
class JsonPathEnv(Env):
    """
    An environment like those that map names
    to variables, but supporting dereferencing
    an JsonPath expression. Note that it never
    fails a lookup, but always returns an empty 
    list.

    It also interns all parsed expressions
    """
    def __init__(self, bindings=None):
        self.__bindings = bindings or {}
        
        # Currently hardcoded because it is a global is jsonpath-rw
        # Probably not widely used, but will require refactor if so
        jsonpath.auto_id_field = "id"

    def parse(self, jsonpath_string):
        if jsonpath_string not in JSONPATH_CACHE:
            JSONPATH_CACHE[jsonpath_string] = parse_jsonpath(jsonpath_string)
        return JSONPATH_CACHE[jsonpath_string]
        
    def lookup(self, name):
        "str|JsonPath -> ??"
        if isinstance(name, six.string_types):
            jsonpath_expr = self.parse(name)
        elif isinstance(name, jsonpath.JSONPath):
            jsonpath_expr = name
        else:
            raise NotImplementedError() 

        def iter(jsonpath_expr=jsonpath_expr): # Capture closure
            for datum in jsonpath_expr.find(self.__bindings):
                # HACK: The auto id from jsonpath_rw is good, but we lose it when we do .value here,
                # so just slap it on if not present
                if isinstance(datum.value, dict) and 'id' not in datum.value:
                    datum.value['id'] = jsonpath.AutoIdForDatum(datum).value
                yield datum
        return RepeatableIterator(iter)

    def bind(self, *args):
        "(str, ??) -> Env | ({str: ??}) -> Env"
        
        new_bindings = dict(self.__bindings)
        if isinstance(args[0], dict):
            new_bindings.update(args[0])
            return self.__class__(new_bindings)
        
        elif isinstance(args[0], six.string_types):
            new_bindings[args[0]] = args[1]
            return self.__class__(new_bindings)

        else:
            raise ValueError('Bad args to Env.bind')

    def replace(self, data):
        return self.__class__(data)

    def emit_table(self, table_spec):
        raise CannotEmit()

    def emitted_tables(self):
        return []

#
# Actual concrete environments, basically with built-in functions.
#

class BuiltInEnv(DictEnv):
    """
    A built-in environment of operators and functions
    which does not support replacement or bindings.

    For convenience, this environment has been chosen to
    queue up tables to be written out, since it will be
    the first env involved in almost any situation.
    """
    
    def __init__(self):
        self.__tables = []
        return super(BuiltInEnv, self).__init__({
            '+'   : operator.__add__,
            '-'   : operator.__sub__,
            '*'   : operator.__mul__,
            '//'  : operator.__floordiv__,
            '/'   : operator.__truediv__,
            '>'   : operator.__gt__,
            '>='  : operator.__ge__,
            '<'   : operator.__lt__,
            '<='  : operator.__le__,
            'len' : len,
            'bool': bool,
        })

    def bind(self, name, value): raise CannotBind()
    def replace(self, data): raise CannotReplace()

    def emit_table(self, table):
        self.__tables.append(table)

    def emitted_tables(self):
        return self.__tables

