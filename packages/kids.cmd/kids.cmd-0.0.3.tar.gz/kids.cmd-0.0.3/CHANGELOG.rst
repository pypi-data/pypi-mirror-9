Changelog
=========

0.0.3 (2015-03-12)
------------------

New
~~~

- [cmd] add ``exname`` to args ``__env__`` sent to sub commands.
  [Valentin Lab]

- [cmd] catches uncaught exception and hide the full traceback except if
  debug environment variable set. [Valentin Lab]

Changes
~~~~~~~

- [cmd] ``.cfg`` provides read/write access to config files. [Valentin
  Lab]

Fix
~~~

- [menu] line call would fail because of incorrect call to
  ``kids.ansi``. [Valentin Lab]

- Fixed bunch of bugs on argument attribution. [Valentin Lab]

  Added thorough tests on the facility.

0.0.2 (2015-02-06)
------------------

- First import. [Valentin Lab]


