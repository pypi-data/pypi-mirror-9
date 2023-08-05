:mod:`zuice.bindings`
=====================

.. module:: zuice.bindings

.. class:: Bindings

    .. method:: bind(key)
    
        Create a :class:`Binder` for the given key. 
    
    .. method:: copy()
    
        Create a copy of this :class:`Bindings` instance. Any further modifications
        to this instance will not modify the copy, and vice versa.
    
    .. method:: __contains__(key)
    
        Return :keyword:`True` if the key has been bound; :keyword:`False` otherwise.
    
    .. method:: __getitem__(key)
    
        If the key has been bound, return the provider for that key. Otherwise,
        raise :class:`KeyError`.

.. class:: Binder

    Each :class:`Binder` is created with a key. When using Zuice, you will rarely
    need to assign a :class:`Binder` to a variable. For instance, instead of::
    
        binder = bindings.bind("spam")
        binder.to_type(Spam)
        
    simply write::
    
        bindings.bind("spam").to_type(Spam)
        
    .. method:: to_provider(provider)
    
        The most powerful of all methods on :class:`Binder`, all other methods simply
        delegate to this one by creating various providers. A provider is a function
        that returns an instance for the key given an injector.
        
        For instance, let's say whenever we attempt to inject the name ``uuid_generator``,
        we want to return ``uuid.uuid4``. We could write this as::
        
            bindings.bind('uuid_generator').to_provider(lambda injector: uuid.uuid4)
            
        In this case, there is a convenience method, :func:`to_instance`, that
        has the same effect.
        
    .. method:: to_instance(instance)
    
        Bind the key to a specific instance. Whenever the injector attempts to
        get an instance associated with the key, this same instance will always
        be returned. Equivalent to calling ``to_provider(lambda injector: instance)``.
    
    .. method:: to_key(key)
    
        Bind the key to another key. Roughly equivalent to calling
        ``to_provider(lambda injector: injector.get(key))``.
    
    .. method:: to_type(key)
    
        Synonym of :func:`~zuice.bindings.Binder.to_key`.
