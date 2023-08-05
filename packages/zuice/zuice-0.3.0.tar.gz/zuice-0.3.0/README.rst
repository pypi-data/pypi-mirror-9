Zuice: dependency injection for Python
======================================

Example
-------

.. code-block:: python

    import zuice

    class BlogPostLister(zuice.Base):
        _fetcher = zuice.dependency(BlogPostFetcher)

        def all(self):
            return ", ".join(post.name for post in self._fetcher.fetch_all())

    bindings = zuice.Bindings()
    bindings.bind(BlogPostFetcher).to_instance(blog_post_fetcher)

    injector = zuice.Injector(bindings)
    assert injector.get(BlogPostFetcher) is blog_post_fetcher
    injector.get(BlogPostLister) # constructs BlogPostLister using the bound instance of BlogPostFetcher

