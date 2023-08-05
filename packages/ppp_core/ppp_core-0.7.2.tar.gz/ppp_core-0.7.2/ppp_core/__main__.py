
import asyncore
from .router import Router
from ppp_libmodule.async_http import Router as HttpRouter

server = HttpRouter('localhost', 9000, Router)
asyncore.loop()
