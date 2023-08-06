Target Host
===========

For the implementation of the following discussion see
:meth:`~gabbi.driver.build_tests`.

Gabbi intends to preserve the flow and semantics of HTTP interactions
as much as possible. Every HTTP request needs to be directed at a host
of some form. Gabbi provides three ways to control this:

* Using `wsgi-intercept`_ to provide a fake socket and ``WSGI``
  environment on an arbitrary host and port attached to a ``WSGI``
  application (see `intercept examples`_).
* Using fully qualified ``url`` values in the YAML defined tests (see
  `full examples`_).
* Using a host and (optionally) port defined at test build time (see
  `live examples`_).

Intercept and live are mutually exclusive per test builder, but either
kind of test can freely intermix fully qualified URLs into the
sequence of tests in a YAML file.

For test driven development and local tests the intercept style of
testing lowers test requirements (no web server required) and is fast.
Interception is performed as part of fixture processing as the most
deeply nested fixture. This allows any configuration or database
setup to be performed prior to the WSGI application being created.

.. _wsgi-intercept: https://pypi.python.org/pypi/wsgi_intercept
.. _intercept examples: https://github.com/cdent/gabbi/blob/master/gabbi/test_intercept.py
.. _full examples: https://github.com/cdent/gabbi/blob/master/gabbi/gabbits_intercept/google.yaml
.. _live examples: https://github.com/cdent/gabbi/blob/master/gabbi/test_live.py
