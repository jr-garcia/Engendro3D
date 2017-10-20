import os
import sys
from importlib import import_module


def resolve_import(local=False):
    try:
        if local or not import_module('e3d'):
            raise ImportError('')
        else:
            print('Engendro3D found on PythonPath.')
    except ImportError:
        if local:
            print('Forcing local copy.')
        else:
            print('Engendro3D not found on PythonPath. Setting local copy.')
        module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        if module_path not in sys.path:
            sys.path.append(module_path)

