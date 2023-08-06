#! /usr/bin/env python
try:
    from titley import titley
except ImportError:
    import os.path
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from titley import titley
    
titley.main()
