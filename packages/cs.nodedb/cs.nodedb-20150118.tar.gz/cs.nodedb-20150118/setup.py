#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.nodedb',
  description = 'a simple and versatile collection of nodes with attributes, accessed as direct Python objects and automatically transcribed to assorted backing stores (CSV, SQL, GDBM, etc); the CSV backend can be (loosely) shared between multiple clients',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'NodeDB: a collection of native Python objects with backing store\n================================================================\n\nA NodeDB is a base class for (currently small) databases of Node objects, native Python objects identified by their .type and .name attributes, and with uppercase attributes.\n\nNode attribute access\n---------------------\n\nAs far as the backing store goes, each attribute is a sequence of values. Within Python, an attribute may be directly accessed as .FOO, which returns element 0 if the value sequence and requires the sequence to have exactly one element, or as .FOOs or .FOOes (note the lowercase plural suffix) which returns a view of the whole sequence.\n\nThe plural forms return a sequence view which itself accepts .FOO or .FOOs attributes. If the values are all Nodes, .FOOs returns a new view with all the .FOO values from each Node, so one may cascade access through a graph of Nodes, example::\n\n  N.LIST_MEMBERs.EMAIL_ADDRESSes\n\nwhich might return a sequence of email addresses from all the .LIST_MEMBER values from the root Node `N`.\n\nThe Node attributes obey both the sequence API and some of the set API: you can .append to or .extend one, or .add to or .update as with a set::\n\n  M = MemberNode("bill")\n  N.LIST_MEMBERs.add(M)\n\nBacking Stores\n--------------\n\nA NodeDB can be backed by a CSV file (beta quality - I use it myself extensively) or SQL or a DBM file (alpha quality, both need some work). The CSV backend allows multiple clients to share the file; they update by appending to the file and monitor the updates of others.\n',
  package_dir = {'': 'lib/python'},
  packages = ['cs.nodedb'],
  requires = ['cs.csvutils', 'cs.debug', 'cs.excutils', 'cs.fileutils', 'cs.html', 'cs.lex', 'cs.logutils', 'cs.obj', 'cs.py.func', 'cs.py3', 'cs.seq', 'cs.sh', 'cs.threads', 'cs.timeutils'],
)
