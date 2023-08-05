About
=====

This module is sort of like os.walk on steroids. It was created to allow the safe use of command-line path arguments in your Python scripts. For instance, say the user passes in several files and directories as arguments and you want to return a sorted list of files within said directories meeting specific access, extension, and/or size criteria. Or perhaps the user passes in a list of files and you want to verify that all of the files meet the necessary criteria before using them.


Installation
============

::

   pip3 install batchpath

The :code:`batchpath` module is known to be compatible with Python 3.

NOTE: This module uses os.walk(), but will use scandir's significantly faster implementation if it is available. Consider installing the **scandir** module.


Usage
=====

.. code:: python

  from batchpath import GeneratePaths()

  gp = GeneratePaths()
  paths = ['/path/to/directory']
  files = gp.files(paths, access=os.R_OK, extensions=['conf','txt'], minsize=0, recursion=True)


.. code:: python

  from batchpath import VerifyPaths()

  vp = VerifyPaths()
  paths = ['/path/to/file', '/path/to/dir', '/path/to/other']
  verification_status = vp.all(paths, access=os.R_OK)
  invalid_paths = vp.failures


License
=======

Copyright (c) 2015 Six (brbsix@gmail.com).

Licensed under the GPLv3 license.
