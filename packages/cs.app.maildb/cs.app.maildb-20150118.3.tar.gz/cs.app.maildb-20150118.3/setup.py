#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.app.maildb',
  description = 'a cs.nodedb NodeDB subclass for storing email address information (groups, addresses, so forth)',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118.3',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  entry_points = {'console_scripts': ['maildb = cs.app.maildb:main']},
  keywords = ['python2', 'python3'],
  long_description = u'MailDB: NodeDB subclass for storing email information.\n======================================================\n\nA MailDB is a subclass of the NodeDB from cs.nodedb; I use it to manage my mail address database and groups (from while mail aliases are generated and which mail filing rules consult).\n\nIt comes with a script named "maildb" for editing the database and performing various routine tasks such as learning all the addresses from a mail message or emitting mail alias definitions, particularly for mutt.\n\nA MailDB knows about an assortment of Node types and has Node subclasses for these with convenience methods for suitable tasks; creating a Node with a the type "ADDRESS", for example, instantiates an AddressNode.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.app.maildb'],
  requires = ['cs.logutils', 'cs.mailutils', 'cs.nodedb', 'cs.lex', 'cs.sh', 'cs.threads', 'cs.py.func', 'cs.py3'],
)
