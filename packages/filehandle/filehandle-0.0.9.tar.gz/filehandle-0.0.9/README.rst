.. image:: https://travis-ci.org/necrolyte2/filehandle.svg
     :target: https://travis-ci.org/necrolyte2/filehandle

.. image:: https://coveralls.io/repos/necrolyte2/filehandle/badge.svg
     :target: https://coveralls.io/r/necrolyte2/filehandle

.. image:: https://badge.fury.io/py/filehandle.svg
       :target: https://badge.fury.io/py/filehandle

filehandle
==========

Normalize the way you get file handle from either gzip or normal file

Typical way to open gzip or regular file

.. code-block:: python

    >>> import gzip
    >>> import os.path
    >>> files = ['/path/to/foo.bar.gz', '/path/to/foo.bar']
    >>> for f in files:
    ...   root, ext = os.path.splitext(f.replace('.gz',''))
    ...   ext = ext[1:]
    ...   if f.endswith('.gz'):
    ...     handle = gzip.open(f)
    ...   else:
    ...     handle = open(f)

Using filehandle
----------------

.. code-block:: python

    >>> import filehandle
    >>> files = ['/path/to/foo.bar.gz', '/path/to/foo.bar']
    >>> for f in files:
    ...   handle, extension = filehandle.open(f)
