import os
import sys
__path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if __path not in sys.path:
    sys.path.insert(0, __path)