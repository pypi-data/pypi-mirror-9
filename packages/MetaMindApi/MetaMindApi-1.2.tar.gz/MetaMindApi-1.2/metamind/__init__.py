# Python 3 compatibility hack
import sys
if sys.version_info[0] == 3:
  __builtins__.xrange = range
  __builtins__.basestring = str
  __builtins__.unicode = str