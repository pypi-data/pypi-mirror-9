#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.id3',
  description = "support for ID3 tags, mostly a convenience wrapper for Doug Zongker's pyid3lib",
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116.2',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"Support for ID3 tags.\n=====================\n\nThis module is mostly a convenience wrapper for Doug Zongker's pyid3lib. Note that pyid3lib is not on PyPI and must be fetched independently.\n\nI'm utilising it via cs.id3 in my id3ise script (https://bitbucket.org/cameron_simpson/css/src/tip/bin-cs/id3ise), yet another MP3 tagger/cleaner script. See that script for how to use the ID3 class.\n\nThe ID3 class has a much wider suite of convenience attribute names and several convenience facilities.\n\nReferences:\n===========\n\nDoug Zongker's pyid3lib:\n    http://pyid3lib.sourceforge.net/\n\nMy id3ise script:\n    https://bitbucket.org/cameron_simpson/css/src/tip/bin-cs/id3ise\n\nid3 2.3.0 spec, frames:\n    http://id3.org/id3v2.3.0#Text_information_frames\n\nid3 2.4.0 spec, frames:\n    http://id3.org/id3v2.4.0-frames\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.id3'],
  requires = ['cs.logutils', 'cs.threads', 'cs.obj'],
)
