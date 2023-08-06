Changelog
=========

0.0.4 (2015-03-04)
------------------

New
~~~

- Nearly all commands now support list of filenames. [Valentin Lab]

0.0.3 (2015-02-06)
------------------

New
~~~

- Added ``File`` to read files by chunk delimited by any char. [Valentin
  Lab]

  Standard file object's method ``.read()`` return line by line content,
  but there is no way to parse with having a delimiter other than ``\n``
  or equivalent. This is what ``File`` does.


- Added ``normpath`` that support a ``cwd`` argument. [Valentin Lab]

- ``basename`` now supports multiple suffixes. [Valentin Lab]

- [chk] added shortcut ``is_dir`` ``is_file`` ``exists``. [Valentin Lab]

  These are only a way to gather them in ``chk`` and rename names
  to follow pep8 conventions.


0.0.2 (2015-01-20)
------------------

New
~~~

- [basename] added a full basename support (with suffix removal).
  [Valentin Lab]

- [chown] walk in alphabetical order and support setting only user or
  group, and support of numerical ids. [Valentin Lab]

- Big changes to the API, ``rmtree`` now in ``rm``, ``zip_file`` return
  filename. [Valentin Lab]

0.0.1 (2013-02-12)
------------------

- First import. [Valentin Lab]


