"""Blueprint for the /packages endpoint.

If a package is *not* in the ``PRIVATE_EGGS`` set, pryvate will redirect
the client to another CheeseShop. However if a package *is* in
``PRIVATE_EGGS`` but the ``filename`` is not available, it will return
a ``404`` response, otherwise it will return a ``200`` response with the
contents of ``filename``
"""
