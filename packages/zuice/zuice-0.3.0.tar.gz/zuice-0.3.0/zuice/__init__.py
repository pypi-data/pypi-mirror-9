import itertools

import zuice.reflect
from .bindings import Bindings

__all__ = ['Bindings', 'Injector', 'Base', 'dependency']


class _Scope(object):
    def __init__(self, active_values, cached_values=None):
        if cached_values is None:
            cached_values = {}
        
        self._active_values = active_values
        self._active_key = frozenset(self._active_values.items())
        self._active_scope_key = frozenset(self._active_values.keys())
        self._cached_values = cached_values
    
    def __contains__(self, key):
        return key in self._active_values
    
    def get(self, key):
        return self._active_values[key]
    
    def enter(self, instances):
        active_values = self._active_values.copy()
        active_values.update(instances)
        new_scope = _Scope(active_values, self._cached_values)
        return new_scope
    
    def cache_get(self, key, provide):
        cache_key = (key, self._active_key)
        if cache_key not in self._cached_values:
            self._cached_values[cache_key] = provide()
            
        return self._cached_values[cache_key]
    
    def in_scope(self, scope_keys):
        active_values = dict(
            (key, self._active_values[key])
            for key in scope_keys
        )
        return _Scope(active_values, self._cached_values)


class Injector(object):
    def __init__(self, bindings, _scope=None):
        self._bindings = bindings.copy()
        if _scope is None:
            _scope = _Scope({})
            
        self._scope = _scope
    
    def get(self, key, instances=None):
        if instances:
            injector = self._extend_with_instances(instances)
            return injector.get(key)
        else:
            return self._get_by_key(key)
    
    def _extend_with_instances(self, instances):
        return Injector(self._bindings, self._scope.enter(instances))
    
    def _get_by_key(self, key):
        if key == Injector:
            return self
        
        elif key in self._scope:
            return self._scope.get(key)
        
        elif key in self._bindings:
            return self._get_from_binding(key, self._bindings[key])
            
        elif isinstance(key, type):
            return self._get_from_type(key)
        
        elif isinstance(key, _Factory):
            return lambda instances: self.get(key._key, instances)
        
        else:
            raise NoSuchBindingException(key)
    
    def _get_from_binding(self, key, binding):
        if binding.scope_key is None:
            return binding.provider(self)
        else:
            if self._scope._active_scope_key == frozenset(binding.scope_key):
                return self._scope.cache_get(key, lambda: binding.provider(self))
            else:
                injector = self._in_scope(binding.scope_key)
                return injector.get(key)
    
    def _in_scope(self, scope_keys):
        scope = self._scope.in_scope(scope_keys)
        return Injector(self._bindings, scope)
    
    def _get_from_type(self, type_to_get):
        if hasattr(type_to_get.__init__, '_zuice'):
            return type_to_get(___injector=self)
        
        elif zuice.reflect.has_no_arg_constructor(type_to_get):
            return type_to_get()
        
        else:
            raise NoSuchBindingException(type_to_get)


class NoSuchBindingException(Exception):
    def __init__(self, key):
        self.key = key
        
    def __str__(self):
        return str(self.key)


_param_counter = itertools.count(1)


class _Parameter(object):
    pass


class _Dependency(_Parameter):
    def __init__(self, key):
        self._key = key
        self._ordering = next(_param_counter)
    
    def inject(self, injector):
        return injector.get(self._key)


def dependency(key):
    return _Dependency(key)


class _Key(object):
    def __init__(self, name):
        self._name = name
    
    def __repr__(self):
        return "Key({0})".format(repr(self._name))
    

def key(name):
    return _Key(name)


class Base(object):
    def __init__(self, *args, **kwargs):
        attrs = [(key, getattr(self, key)) for key in dir(type(self))]
        
        params = [
            (key, attr)
            for (key, attr) in attrs
            if isinstance(attr, _Parameter)
        ]
        if '___injector' in kwargs:
            injector = kwargs.pop('___injector')
            for key, attr in params:
                setattr(self, key, attr.inject(injector))
        else:
            _manual_injection(self, params, args, kwargs)
        
        inits = sorted(
            (attr for key, attr in attrs if hasattr(attr, "_zuice_init")),
            key=lambda attr: attr._zuice_init
        )
        for init in inits:
            init()
        
        _check_keyword_arguments_consumed(kwargs)
    
    __init__._zuice = True


def _manual_injection(self, attrs, args, kwargs):
    if len(args) > len(attrs):
        raise TypeError(
            "__init__ takes exactly %s arguments (%s given)" %
                (len(attrs) + 1, len(args) + 1)
        )
    attrs.sort(key=lambda item: item[1]._ordering)
    for index, (key, attr) in enumerate(attrs):
        arg_name = _key_to_arg_name(key)
        
        if index < len(args):
            if arg_name in kwargs:
                raise TypeError("Got multiple values for keyword argument '%s'" % arg_name)
            setattr(self, key, args[index])
        elif arg_name in kwargs:
            setattr(self, key, kwargs.pop(arg_name))
        else:
            raise _missing_keyword_argument_error(arg_name)
    


def _key_to_arg_name(key):
    return key.lstrip("_")


def _missing_keyword_argument_error(key):
    return TypeError("Missing keyword argument: %s" % key)


def _unexpected_keyword_argument_error(key):
    raise TypeError("Unexpected keyword argument: " + key)


def _check_keyword_arguments_consumed(kwargs):
    if len(kwargs) > 0:
        raise _unexpected_keyword_argument_error(next(iter(kwargs.keys())))
    

def init(func):
    func._zuice_init = next(_param_counter)
    return func


def factory(key):
    return _Factory(key)


class _Factory(object):
    def __init__(self, key):
        self._key = key
    
    def __repr__(self):
        return "factory({0})".format(self._key)
