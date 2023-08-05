"""Private PyPi repository and proxy.

Pryvate tries to only handle private packages with the least
amount of magic, if it cannot serve a request itself it will
redirect the client to another CheeseShop.
"""
from .server import run
