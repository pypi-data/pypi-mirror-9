dirsync - Changes
=================


2.2 (28-01-2015)
----------------

Fixed:
- [cmdline] Package name is now consistently displayed in console messages
- [cmdline] Traceback is no longer shown when an exception is raised
- Nicer error messages
- Created directories counter now works

Changed:
- [backwards incompatible]: --nodirection option replaced by --twoway (-2)
- [backwards incompatible]: --modtimeonly option replaced by --ctime
  (defaults to False)
- A default ~/.dirsync config file is created on first run


2.1 (08-09-2014)
----------------

- Added config files support when called from command line
- Added custom logger when called from python


2.0 (30-07-2014)
----------------

- The script is now wrapped into a python package
- ``ignore``, ``exclude``, ``only`` and ``include`` options for advanced file
  filtering via regular expressions
- Python 3 compatibility


1.0 (30-10-2003)
----------------

- Anand's Python robocopier is published on activestate:
  http://code.activestate.com/recipes/231501-python-robocopier-advanced-directory-synchronizati/
