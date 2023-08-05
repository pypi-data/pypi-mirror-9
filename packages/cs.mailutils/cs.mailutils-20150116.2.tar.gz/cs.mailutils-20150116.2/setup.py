#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.mailutils',
  description = 'functions and classes to work with email',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116.2',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Functions and classes to work with email.\n=========================================\n\n* Maildir: a much faster subclass of mailbox.Maildir, because you really can trust the output of os.listdir to scan for changes\n\n* Message(msgfile, headersonly=False): factory function to accept a file or filename and return an email.message.Message\n\n* ismaildir(path): test if `path` refers to a Maildir\n\n* ismbox(path): test if `path` refers to an mbox file\n\n* ismhdir(path): test if `path` refers to an MH mail folder\n\n* make_maildir(path): create a new Maildir\n\n* message_addresses(M, header_names): generator that yields (realname, address) pairs from all the named headers\n\n* modify_header(M, hdr, new_value, always=False): modify a Message `M` to change the value of the named header `hdr` to the new value `new_value`\n\n* shortpath(path, environ=None): use cs.lex.shortpath to return a short refernce to a mail folder using $MAILDIR for "+" and $HOME for "~"\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.mailutils'],
  requires = ['cs.fileutils', 'cs.logutils', 'cs.threads', 'cs.seq', 'cs.py3'],
)
