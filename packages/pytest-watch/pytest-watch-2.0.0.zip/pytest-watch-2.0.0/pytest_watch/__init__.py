"""\
pytest_watch
------------

Local continuous test runner with pytest and watchdog.

:copyright: (c) 2015 by Joe Esposito.
:license: MIT, see LICENSE for more details.
"""

__version__ = '2.0.0'


from . import command
from .watcher import watch
