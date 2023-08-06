Edi
===

::

  ~/yourgitrepo$ edi first buried file
  Loading:
  - ~/yourgitrepo/your/first/file/very/deep/and/buried/somewhere.txt

If there is *only one* file matching your key words then it is opened straight away in your text editor.


::

  ~/yourgitrepo$ edi buried file
  ./a/third/**file**/very/deep/and/**buried**/somewhere.txt
  ./a/second/**file**/very/deep/and/**buried**/somewhere.txt
  ./a/first/**file**/very/deep/and/**buried**/somewhere.txt


Multiple matching files are listed in reverse modification order.

::

  ~/yourgitrepo$ edi buried file l
  Loading:
  - ./a/third/file/very/deep/and/buried/somewhere.txt)

Add the letter l at the end to load the last modified matching file.



Install
=======

$ sudo pip install edi

Configure
=========

By default, edi will invoke your system's default text editor.

If you have a .edi.yml file somewhere beneath your current location,
it will invoke the command from that instead, using {0} as an argument.

See some examples in the examples_configs/ folder.
