#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.serialise',
  description = 'some serialisation functions',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Some serialisation functions.\n=============================\n\nI use these functions to serialise and de-serialise non-negative integers of arbitrary size and run length encoded block data.\n\nThe integers are encoded as octets in big-endian order, with the high bit indicating that more octets follow.\n\n* get_bs(bs, offset=0): collect an integer from the bytes `bs` at the specified `offset`\n\n* get_bsdata(bs, offset=0): collect a run length encoded data block from the bytes `bs` at the specified `offset`\n\n* get_bsfp(fp): collect an integer from the binary file `fp`\n\n* put_bs(n): return the bytes encoding of the supplied integer `n`\n\n* put_bsdata(data): return the bytes run length encoding of the supplied data block\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.serialise'],
)
