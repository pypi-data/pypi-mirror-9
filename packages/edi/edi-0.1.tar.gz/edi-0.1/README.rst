Edi
===

  ~/yourgitrepo$ edi first buried file

(opens ~/yourgitrepo/your/**first**/**file**/very/deep/and/**buried**/somewhere.txt)

If there is *only one* file matching your key words then it is opened straight away in your text editor.


  ~/yourgitrepo$ edi buried file

./a/third/**file**/very/deep/and/**buried**/somewhere.txt  <-- the last matching file you edited.
./a/second/**file**/very/deep/and/**buried**/somewhere.txt
./a/first/**file**/very/deep/and/**buried**/somewhere.txt

If there are *multiple* files matching your key words then they are listed 
in reverse order of last modification but nothing is opened.


  ~/yourgitrepo$ edi buried file l

(opens ./a/third/**file**/very/deep/and/**buried**/somewhere.txt)

If there are multiple files matching your key words and you append the letter l
then the last modified file matching your key words is opened.



Install
=======

$ sudo pip install edi

Configure
=========

By default, edi will invoke your system's default text editor.

If you have a .edi.yml file somewhere beneath your current location,
it will invoke the command from that instead, using {0} as an argument.

See some examples in the examples_configs/ folder.
