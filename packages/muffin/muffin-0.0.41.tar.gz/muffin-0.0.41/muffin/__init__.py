"""
    muffin description.

"""

# Package information
# ===================

__version__ = "0.0.41"
__project__ = "muffin"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"

from asyncio import *           # noqa

from aiohttp.web import *       # noqa

from .app import Application, CONFIGURATION_ENVIRON_VARIABLE  # noqa
from .handler import Handler    # noqa
from .utils import to_coroutine # noqa
