import sys
import os


def setPath():
    module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    sys.path.append(module_path)
