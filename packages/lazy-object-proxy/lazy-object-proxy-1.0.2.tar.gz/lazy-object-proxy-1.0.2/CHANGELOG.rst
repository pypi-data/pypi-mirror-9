
Changelog
=========

1.0.2 (2015-04-11)
------------------

* Remove the bogus ``lazy_object_proxy`` console script (contributed by Tin Tvrtković in `#4 <https://github.com/ionelmc/python-lazy-object-proxy/pull/4>`_).

1.0.1 (2014-12-28)
------------------

* Fix access via class bug in the ``__wrapped__`` property from ``lazy_object_proxy.simple.Proxy``.

1.0.0 (2014-12-27)
------------------

* General code cleanup
* A faster pure-python Proxy implementation (``lazy_object_proxy.simple.Proxy``) to be used where the C extension is not available. It's not
  a complete proxy so it's never available as ``lazy_object_proxy.Proxy``.

0.1.0 (2014-06-10)
------------------

* First release on PyPI.
