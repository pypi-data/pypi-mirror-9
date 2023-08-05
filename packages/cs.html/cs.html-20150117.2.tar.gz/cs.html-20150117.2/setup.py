#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.html',
  description = 'easy HTML transcription',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150117.2',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'HTML transcription functions.\n=============================\n\nMalformed markup is enraging. Therefore, when I must generate HTML I construct a token structure using natural Python objects (strings, lists, dicts) and use this module to transcribe them to syntacticly correct HTML. This also avoids lots of tediuous and error prone entity escaping.\n\n* tok2s: transcribe tokens to a string; trivial wrapper for puttok\n\n* puttok: transcribe tokens to a file\n\n* text2s: transcribe a string to an HTML-safe string; trivial wrapper for puttext\n\n* puttext: transcribe a string as HTML-safe text to a file\n\n* BR: a convenience token for <br/>, which I use a lot\n\nA "token" in this scheme is:\n\n* a string: transcribed safely to HTML\n\n* an int or float: transcribed safely to HTML\n\n* a preformed token object with .tag (a string) and .attrs (a mapping) attributes\n\n* a sequence: an HTML tag: element 0 is the tag name, element 1 (if a mapping) is the element attributes, any further elements are enclosed tokens\n\n  - because a string like "&foo" gets its "&" transcribed into the entity "&amp;", a single element list whose tag begins with "&" encodes an entity, example: ["&lt;"]\n\nExample::\n\n  from cs.html import puttoken, BR\n  [...]\n  table = [\'TABLE\', {\'width\': \'80%\'},\n           [\'TR\',\n            [\'TD\', \'a truism\'],\n            [\'TD\', \'1 < 2\']\n           ]\n          ]\n  [...]\n  puttoken(sys.stdout,\n            \'Here is a line with a line break.\', BR,\n            \'Here is a trite table.\',\n            table)\n\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.html'],
  requires = ['cs.py3'],
)
