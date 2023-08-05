Changelog
=========

0.1.4 (2015-02-13)
------------------

- Allow for indexing of normal dict and other values as well as I18NDict.
- Better to iterate over the existing indices in case the available language configuration changes.


0.1.3.1 (2014-11-14)
--------------------

- Added en translation.


0.1.3 (2014-11-14)
------------------

- Added translations (de, es).
- Provide the 'Add translation' value already translated (e.g. for JS).


0.1.2 (2014-11-01)
------------------

- Return empty dict when value is None.
- Test for correct value types before we set any data.
- Correctly evaluate the bool value of the I18NDict when the field is required.
- When the fallback is the first value found, sort the values so that the result is consistent with each repeated call.


0.1.1 (2014-09-25)
------------------

- Always return the super call instead of None when no sub-indices have been created yet.
- Add tests to cover the sort method with and without values.


0.1 (2014-09-23)
----------------

- Initial release.
