Changelog
=========

0.0.5 (2015-03-04)
------------------

New
~~~

- Added ``MultiDictReader`` class to allow reading from several dicts.
  [Valentin Lab]

  This provides an interesting lazy evaluated way to merge
  dicts. Additionaly multi-depth dicts are conveniently merged.


- Added ``AttrDictAbstract`` to help creating attr-dict patterns from a
  small method subset. [Valentin Lab]

- Introduce ``DictLikeAbstract`` to write quickly full dict like API
  from a small subset. [Valentin Lab]

- Added ``untokenize`` notion, it'll undo ``tokenize`` job. [Valentin
  Lab]

- ``.items()`` is not flattening anymore, use ``.flat`` for that.
  [Valentin Lab]

  Replaced the flattening of the items done by ``.items()`` to remove it
  towards the ``.flat`` property.

  In the process, the ``.keys()`` was added.


- Dict is now passed by reference and mdict is offering a extended API
  to it. [Valentin Lab]

- [mdict] cleaned code a give a more coherent API. [Valentin Lab]

Fix
~~~

- When iterating through keys of mdict, those weren't appropriately
  quoted. [Valentin Lab]

Other
~~~~~

- Fixup! new: introduce ``DictLikeAbstract`` to write quickly full dict
  like API from a small subset. [Valentin Lab]

0.0.4 (2015-02-06)
------------------

New
~~~

- [dct] added ``deep_copy`` shortcut. [Valentin Lab]

  This is to get all usefull dict related stuff without having to know
  all package required. And to follow pep8 convention on variable/function
  names (aka: deep_copy instead of deepcopy).


- [dct] added ``merge`` to merge dicts. [Valentin Lab]

0.0.3 (2015-02-05)
------------------

New
~~~

- [graph] added ``graph`` functions. [Valentin Lab]

- [mdict] added ``mdict`` pattern. [Valentin Lab]

- [lib] ``half_split_on_predicate`` added. [Valentin Lab]

- [lib] added ``default`` arguments to ``first``. [Valentin Lab]

0.0.2 (2015-01-20)
------------------

New
~~~

- Python3 support and added tests for better coverage. [Valentin Lab]

- [match] added matching and fuzzy matching library. [Valentin Lab]

- [fmt] remove all trailing whitespace on record line display. [Valentin
  Lab]

0.0.1 (2014-05-23)
------------------

- First import. [Valentin Lab]


