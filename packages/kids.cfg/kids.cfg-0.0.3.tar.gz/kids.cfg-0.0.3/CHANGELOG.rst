Changelog
=========

0.0.3 (2015-03-04)
------------------

New
~~~

- Can access conf files not yet created but listed. [Valentin Lab]

  If you had listed a local file in ``REPOS/.foo.rc`` and a global config
  file in ``~/.foo.rc`` then you can store values and access them now via
  ``MConfig`` and the file will then get created.

- Full support YAML, configobj, python config file, and multilayers
  config files. [Valentin Lab]

  - autodetection of syntax
  - 3 syntax provided: YAML, configobj, python config
  - write support provided for: YAML, configobj

Changes
~~~~~~~

- Use ``safe_load`` when parsing Yaml instead of ``load``. [Valentin
  Lab]

  If we have a valid reason to use ``load`` we'll consider putting it
  back.

0.0.2 (2015-03-04)
------------------

New
~~~

- ``MConfig`` object allow read-write access to all config files at
  once. [Valentin Lab]

- Full support YAML, configobj, python config file, and multilayers
  config files. [Valentin Lab]

  - autodetection of syntax
  - 3 syntax provided: YAML, configobj, python config
  - write support provided for: YAML, configobj

Changes
~~~~~~~

- ``find_files`` return now a label for each file coming from the find
  structure. [Valentin Lab]

  This is important to identify the matching pattern and give
  it an identifier.

- Removed the defaut included ``mdict`` interface. [Valentin Lab]

  This interface was conflicting with normal dict interface. Decision
  was taken than ``mdict`` should only be used explicitely and only
  when needed.

Fix
~~~

- Code executed coming from config would loose references. [Valentin
  Lab]

  This is due to ``__builtins__`` being deleted in config. The only
  thing we wanted was actually to output a dict, so the workaround
  is to copy the key, value pairs excepts ``__builtins__``.

0.0.1 (2014-05-14)
------------------

- First import. [Valentin Lab]


