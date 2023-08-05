#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.fileutils',
  description = 'convenience functions and classes for files and filenames/pathnames',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Convenience functions and classes for files and filenames/pathnames.\n====================================================================\n\n* Pathname: subclass of str with convenience properties useful for pathnames\n\n* BackedFile: a RawIOBase implementation that uses a backing file for initial data and writes new data to a front file\n\n* SharedAppendFile: a base class to share a modifiable file between multiple users\n\n* SharedAppendLines: a subclass of SharedAppendFile which shares updates in units oftext lines\n\n* FileState: a signature object for a file state derived from os.stat or os.lstat or os.fstat; has .mtime, .size, .dev and .ino attributes\n\n* abspath_from_file: restore relative path with respect to another path, as for an include filename\n\n* chunks_of: generator yielding text or data from an open file until EOF\n\n* lines_of: generator yielding lines of text from an open file until EOF\n\n* compare: compare two filenames or file-like objects for content equality\n\n* @file_property: decorator for a caching property whose value is recomputed if the file changes\n\n* make_file_property: constructor for variants on @file_property\n\n* @files_property: decorator for a caching property whose value is recomputed if any of a set of files changes\n\n* make_files_property: constructor for variants on @files_property\n\n* lockfile: context manager to take a lock file around an operation, such as access to a shared file\n\n* shortpath: return `path` with the first matching leading prefix replaced with short form such as "~/" or "$LOGDIR/" etc\n\n* longpath: the inverse of shortpath\n\n* mkdirn: create a new directory named path+sep+n, where `n` exceeds any name already present\n\n* poll_file: watch a file for modification by polling its state as obtained by FileState\n\n* rewrite: rewrite the content of a file if changed; with an assortment of modes\n\n* rewrite_cmgr: a context manager made from rewrite()\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.fileutils'],
  requires = ['cs.asynchron', 'cs.debug', 'cs.env', 'cs.logutils', 'cs.queues', 'cs.range', 'cs.threads', 'cs.timeutils', 'cs.obj', 'cs.py3'],
)
