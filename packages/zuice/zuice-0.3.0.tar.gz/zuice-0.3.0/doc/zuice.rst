:mod:`zuice`
============

.. module:: zuice

.. class:: Injector

    .. method:: __init__(bindings)
    
        Create an injector with the given bindings, which is assumed to be of
        type :class:`~zuice.bindings.Bindings`
    
    .. method:: get(key)
        If *key* has been bound, use the bound provider.
        
        Otherwise, if *key* is a type that inherits from :class:`~zuice.Base`,
        attempt to construct the passed type by injecting its dependencies.
        
        Otherwise, if *key* is a type with a zero-argument constructor,
        create an instance using the zero-argument constructor.
        
        Otherwise, raise :class:`~zuice.NoSuchBindingException`.
        
.. class:: Base

    Classes than inherit from :class:`~zuice.Base` will have attributes defined by
    :func:`~zuice.dependency` injected when the class itself is injected. See
    :func:`~zuice.dependency`.
    
.. function:: dependency(key)

    Defines the keys with which attributes are to be injected. For instance::
    
        class PriceCalculator(Base):
            _price_fetcher = dependency(PriceFetcher)
    
        price_calculator = injector.get(PriceCalculator)
        
    is roughly equivalent to::
    
        class PriceCalculator(object):
            def __init__(self, price_fetcher):
                self._price_fetcher = price_fetcher
        
        price_calculator = PriceCalculator(injector.get(PriceFetcher))
        
