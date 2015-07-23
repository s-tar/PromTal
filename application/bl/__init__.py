import os
import glob

__all__ = []
directory = os.path.dirname(__file__)
modules = glob.glob(directory+"/*.py")

for f in modules:
    f = f.replace("__init__.py", "").replace(directory, "")\
         .replace(".py", "", -1).strip('/').strip('\\')

    if f:
        __all__.append(os.path.basename(f))
