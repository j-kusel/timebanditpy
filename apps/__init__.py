import sys, os, glob
from importlib import import_module
from lib import settings

# make all folders in the 'apps' directory importable
_apps = [os.path.basename(a)[:-3] for a in glob.glob(os.path.dirname(__file__)+'/*.py') if os.path.isfile(a)]
__all__ = [a for a in _apps if a != '__init__' and a in settings.INSTALLED_APPS]
for a in __all__:
    import_module('apps.'+a)

# make a list of all app docstrings
