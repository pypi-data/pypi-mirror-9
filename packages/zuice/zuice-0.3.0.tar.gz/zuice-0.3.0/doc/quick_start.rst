Quick Start
===========

Let's say that we have a :class:`PriceCalculator` class that works out the prices
of various commodities using a :class:`DatabasePriceFetcher`::

    class PriceCalculator(object):
        def __init__(self):
            self._price_fetcher = DatabasePriceFetcher()
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
            
So we could, for instance, find the price of 10 apples using 
``price_calculator.price_of(apples, 10)``.

We can use an :class:`~zuice.Injector` to construct a :class:`PriceCalculator`
for us since its constructor takes no arguments::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)

Since :class:`~zuice.Injector` can construct a :class:`PriceCalculator`, we
say that the type :class:`PriceCalculator` is injectable.

However, we might decide that we want to pass in a :class:`DatabasePriceFetcher` instead
of constructing it ourselves -- for instance, this makes the class more easily
tested.

We rewrite :class:`PriceCalcuator` as::

    class PriceCalculator(object):
        def __init__(self, price_fetcher):
            self._price_fetcher = price_fetcher
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

Zuice can no longer construct an instance of :class:`PriceCalculator` for us
-- it does not know how to inject the argument ``price_fetcher``.

Binding instances
^^^^^^^^^^^^^^^^^

The first solution is to manually construct an instance of :class:`PriceCalculator`,
and bind this instance to the type::

    from zuice import Injector
    from zuice import Bindings

    # Assume we've already constructed an instance of PriceCalculator as price_calculator
    bindings = Bindings()
    bindings.bind(PriceCalculator).to_instance(price_calculator)
    injector = Injector(bindings)
    
    injector.get(PriceCalculator) # This returns the same instance of PriceCalculator i.e. price_calculator
    
However, having to construct instances for every type we want to be able to
inject is tedious. Fortunately, we can instead tell Zuice how to inject the
argument ``price_fetcher``.

Binding types
^^^^^^^^^^^^^

We can tell Zuice that ``PriceCalculator`` depends on ``DatabasePriceFetcher``
by inheriting from ``zuice.Base`` and using ``zuice.dependency``::

    import zuice

    class PriceCalculator(zuice.Base):
        _price_fetcher = zuice.dependency(DatabasePriceFetcher)
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number

We can now get an instance of :class:`PriceCalculator`,
assuming that :class:`DatabasePriceFetcher` is already injectable::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    injector = Injector(bindings)
    
    injector.get(PriceCalculator) # This returns a new instance of PriceCalculator
    
This method has the disadvantage that we have now bound :class:`PriceCalculator`
to a specific implementation. What if we wanted to use another class that
behaves in the same manner as :class:`DatabasePriceFetcher`?

One solution is to define a generic type :class:`PriceFetcher`. This might be
as simple as::

    class PriceFetcher(object):
        pass

We then write :class:`PriceCalculator` as::

    import zuice

    class PriceCalculator(zuice.Base):
        _price_fetcher = zuice.dependency(PriceFetcher)
    
        def price_of(self, commodity, number):
            price = self._price_fetcher.price_of(commodity)
            return price * number
    
Finally, to inject a :class:`PriceCalculator`::

    from zuice import Injector
    from zuice.bindings import Bindings

    bindings = Bindings()
    bindings.bind(PriceFetcher).to_type(DatabasePriceFetcher)
    injector = Injector(bindings)
    price_calculator = injector.get(PriceCalculator)
    
    price = price_calculator.price_of(apples, 10)

Now, whenever a :class:`PriceFetcher` needs to be injected, Zuice will inject a
:class:`DatabasePriceFetcher`. If we decide to use a different implementation,
then we can simple change the binding in this one location.
