Changelog
=========

0.5.0 (2015-02-04)
------------------

- FIX: 0.4.0 is released, no need to specify 0.3.1 in README. [Josh
  Warner (Mac)]

- Fixed a small typo. [Rostislav Semenov]

- Reset `processor` and `scorer` defaults to None with argument
  checking. [foxxyz]

- Catch generators without lengths. [Jeremiah Lowin]

- Fixed python3 issue and deprecated assertion method. [foxxyz]

- Fixed some docstrings, typos, python3 string method compatibility,
  some errors that crept in during rebase. [foxxyz]

- [mod] The lamdba in extract is not needed. [Olivier Le Thanh Duong]

  [mod] Pass directly the defaults functions in the args

  [mod] itertools.takewhile() can handle empty list just fine no need to test for it

  [mod] Shorten extractOne by removing double if

  [mod] Use a list comprehention in extract()

  [mod] Autopep8 on process.py

  [doc] Document make_type_consistent

  [mod] bad_chars shortened

  [enh] Move regex compilation outside the method, otherwhise we don't get the benefit from it

  [mod] Don't need all the blah just to redefine method from string module

  [mod] Remove unused import

  [mod] Autopep8 on string_processing.py

  [mod] Rewrote asciidammit without recursion to make it more readable

  [mod] Autopep8 on utils.py

  [mod] Remove unused import

  [doc] Add some doc to fuzz.py

  [mod] Move the code to sort string in a separate function

  [doc] Docstrings for WRatio, UWRatio


- Add note on which package to install. Closes #67. [Jose Diaz-Gonzalez]

0.4.0 (2014-10-31)
------------------

- In extarctBests() and extractOne() use '>=' instead of '>' [Юрий
  Пайков]

- Fixed python3 issue with SequenceMatcher import. [Юрий Пайков]

0.3.3 (2014-10-22)
------------------

- Fixed issue #59 - "partial" parameter for `_token_set()` is now
  honored. [Юрий Пайков]

- Catch generators without lengths. [Jeremiah Lowin]

- Remove explicit check for lists. [Jeremiah Lowin]

  The logic in `process.extract()` should support any Python sequence/iterable. The explicit check for lists is unnecessary and limiting (for example, it forces conversion of generators and other iterable classes to lists).

0.3.2 (2014-09-12)
------------------

- Make release command an executable. [Jose Diaz-Gonzalez]

- Simplify MANIFEST.in. [Jose Diaz-Gonzalez]

- Add a release script. [Jose Diaz-Gonzalez]

- Fix readme codeblock. [Jose Diaz-Gonzalez]

- Minor formatting. [Jose Diaz-Gonzalez]

- Use __version__ from fuzzywuzzy package. [Jose Diaz-Gonzalez]

- Set __version__ constant in __init__.py. [Jose Diaz-Gonzalez]

- Rename LICENSE to LICENSE.txt. [Jose Diaz-Gonzalez]

0.3.0 (2014-08-24)
------------------

- Test dict input to extractOne() [jamesnunn]

- Remove whitespace. [jamesnunn]

- Choices parameter for extract() accepts both dict and list objects.
  [jamesnunn]

- Enable automated testing with Python 3.4. [Corey Farwell]

- Fixed typo: lettters -> letters. [Tal Einat]

- Fixing LICENSE and README's license info. [Dallas Gutauckis]

- Proper ordered list. [Jeff Paine]

- Convert README to rst. [Jeff Paine]

- Add requirements.txt per discussion in #44. [Jeff Paine]

- Add LICENSE TO MANIFEST.in. [Jeff Paine]

- Rename tests.py to more common test_fuzzywuzzy.py. [Jeff Paine]

- Add proper MANIFEST template. [Jeff Paine]

- Remove MANIFEST file Not meant to be kept in version control. [Jeff
  Paine]

- Remove unused file. [Jeff Paine]

- Pep8. [Jeff Paine]

- Pep8 formatting. [Jeff Paine]

- Pep8 formatting. [Jeff Paine]

- Pep8 indentations. [Jeff Paine]

- Pep8 cleanup. [Jeff Paine]

- Pep8. [Jeff Paine]

- Pep8 cleanup. [Jeff Paine]

- Pep8 cleanup. [Jeff Paine]

- Pep8 import style. [Jeff Paine]

- Pep8 import ordering. [Jeff Paine]

- Pep8 import ordering. [Jeff Paine]

- Remove unused module. [Jeff Paine]

- Pep8 import ordering. [Jeff Paine]

- Remove unused module. [Jeff Paine]

- Pep8 import ordering. [Jeff Paine]

- Remove unused imports. [Jeff Paine]

- Remove unused module. [Jeff Paine]

- Remove import * where present. [Jeff Paine]

- Avoid import * [Jeff Paine]

- Add Travis CI badge. [Jeff Paine]

- Remove python 2.4, 2.5 from Travis (not supported) [Jeff Paine]

- Add python 2.4 and 2.5 to Travis. [Jeff Paine]

- Add all supported python versions to travis. [Jeff Paine]

- Bump minor version number. [Jeff Paine]

- Add classifiers for python versions. [Jeff Paine]

- Added note about python-Levenshtein speedup. Closes #34. [Jose Diaz-
  Gonzalez]

- Fixed tests on 2.6. [Grigi]

- Fixed py2.6. [Grigi]

- Force bad_chars to ascii. [Grigi]

- Since importing unicode_literals, u decorator not required on strings
  from py2.6 and up. [Grigi]

- Py3 support without 2to3. [Grigi]

- Created: Added .travis.yml. [futoase]

- [enh] Add docstrings to process.py. [Olivier Le Thanh Duong]

  Turn the existings comments into docstrings so they can be seen via introspection


- Don't condense multiple punctuation characters to a single whitespace.
  this is a behavioral change. [Adam Cohen]

- UQRatio and UWRatio shorthands. [Adam Cohen]

- Version 0.2. [Adam Cohen]

- Unicode/string comparison bug. [Adam Cohen]

- To maintain backwards compatibility, default is to force_ascii as
  before. [Adam Cohen]

- Fix merge conflict. [Adam Cohen]

- New process function: extractBests. [Flávio Juvenal]

- More readable reverse sorting. [Flávio Juvenal]

- Further honoring of force_ascii. [Adam Cohen]

- Indentation fix. [Adam Cohen]

- Handle force_ascii in fuzz methods. [Adam Cohen]

- Add back relevant tests. [Adam Cohen]

- Utility method to make things consistent. [Adam Cohen]

- Re-commit asciidammit and add a parameter to full_process to determine
  behavior. [Adam Cohen]

- Added a test for non letters/digits replacements. [Tristan Launay]

- ENG-741 fixed benchmark line length. [Laurent Erignoux]

- Fixed Unicode flag for tests. [Tristan Launay]

- ENG-741 commented code removed not erased for review from creator.
  [Laurent Erignoux]

- ENG-741 cut long lines in fuzzy wizzy benchmark. [Laurent Erignoux]

- Re-upped the limit on benchmark, now that performance is not an issue
  anymore. [Tristan Launay]

- Fixed comment. [Tristan Launay]

- Simplified processing of strings with built-in regex code in python.
  Also fixed empty string detection in token_sort_ratio. [Tristan
  Launay]

- Proper benchmark display. Introduce methods to explicitly do all the
  unicode preprocessing *before* using fuzz lib. [Tristan Launay]

- ENG-741: having a true benchmark, to see when we improve stuff.
  [Benjamin Combourieu]

- Unicode support in benchmark.py. [Benjamin Combourieu]

- Added file for processing strings. [Tristan Launay]

- Uniform treatment of strings in Unicode. Non-ASCII chars are now
  considered in strings, which allows for matches in Cyrillic, Chinese,
  Greek, etc. [Tristan Launay]

- Fixed bug in _token_set. [Michael Edward]

- Removed reference to PR. [Jose Diaz-Gonzalez]

- Sadist build and virtualenv dirs are not part of the project. [Pedro
  Rodrigues]

- Fixes https://github.com/seatgeek/fuzzywuzzy/issues/10 and correctly
  points to README.textile. [Pedro Rodrigues]

- Info on the pull request. [Pedro Rodrigues]

- Pullstat.us button. [Pedro Rodrigues]

- Fuzzywuzzy really needs better benchmarks. [Pedro Rodrigues]

- Moved tests and benchmarks out of the package. [Pedro Rodrigues]

- Report better ratio()s redundant import try. [Pedro Rodrigues]

- AssertGreater did not exist in python 2.4. [Pedro Rodrigues]

- Remove debug output. [Adam Cohen]

- Looks for python-Levenshtein package, and if present, uses that
  instead of difflib. 10x speedup if present. add benchmarks. [Adam
  Cohen]

- Add gitignore. [Adam Cohen]

- Fix a bug in WRatio, as well as an issue in full_process, which was
  failing on strings with all unicode characters. [Adam Cohen]

- Error in partial_ratio. closes #7. [Adam Cohen]

- Adding some real-life event data for benchmarking. [Adam Cohen]

- Cleaned up utils.py. [Pedro Rodrigues]

- Optimized speed for full_process() [Pedro Rodrigues]

- Speed improvements to asciidammit. [Pedro Rodrigues]

- Removed old versions of validate_string() and remove_ponctuation()
  kept from previous commits. [Pedro Rodrigues]

- Issue #6 from github updated license headers to match MIT license.
  [Pedro Rodrigues]

- Clean up. [Pedro Rodrigues]

- Changes to utils.validate_string() and benchmarks. [Pedro Rodrigues]

- Some benchmarks to test the changes made to remove_punctuation. [Pedro
  Rodrigues]

- Faster remove_punctuation. [Pedro Rodrigues]

- AssertIsNone did not exist in Python 2.4. [Pedro Rodrigues]

- Just adding some simple install instructions for pip. [Chris Dary]

- Check for null/empty strings in QRatio and WRatio. Add tests. Closes
  #3. [Adam Cohen]

- More README. [Adam Cohen]

- README. [Adam Cohen]

- README. [Adam Cohen]

- Slight change to README. [Adam Cohen]

- Some readme. [Adam Cohen]

- Distutils. [Adam Cohen]

- Change directory structure. [Adam Cohen]

- Initial commit. [Adam Cohen]


