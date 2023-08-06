Pyarmor, Guard your python scripts
==================================

Do you worry about how to protect your python scripts?  Now, it's easy
with the coming of Pyarmor.

What's Pyarmor
--------------

A python package could import/run encrypted python scripts.

Pyarmor is designed for developers who do not want distribute literal
python scripts to their customers.

Here are the main differences of using pyarmor to run/import encrypted
python scripts:

* transform python script to encrypted one with extension ".pyx"
* add a few of auxiliary files

It means Pyarmor almost doesn't change anything, you can run/import
encrypted pythons scripts just as they're not encrypted. So you can
run/import encrypted python scripts in any environment which python
can run. For example, in a web framework, or as cgi scripts.

Besides, Pyarmor could run/import encrypted python scripts in target
machine as one of the following ways:

* Any target machine, or
* only in a special machine (bind to hard disk serial number), or
* expried on some day

Pyarmor is command line tool, the main script is "pyarmor.py", you can
run it by python2.6 later.

Supported Python Versions
-------------------------

Pyarmor need python 2.6 or later, but it supports to run/import the
encrypted scripts from Python 2.3 to the latest Python (3.4) by Cross
Publish (See below).

Supported platforms
-------------------

Windows, Linux, including Embeded Linux are supported, The following
operation systems have been tested:

* Windows XP, Windows7 both x86 and amd64
* Ubuntu 13.04 both i686, x86_64 and armv7

Installation
============

* Install corresponding Python
* Run pip to install pyarmor package from pypi.python.org
    $ pip install pyarmor
* Or download the package from pypi.python.org and extract the
  downloaded package to any path, for example, /opt/pyarmor

Wizard
======

There is a gui wizard to show how to use pyarmor, be sure you have
installed python and tkinter, start pyarmor wizard

  $ python wizard.py

The wizard is tested in Python2.7/Python3.2. There are many examples
introduced in this wizard, it's useful to understand all of the
featuers of Pyarmor.

Basic Usage
===========

The normal scenario for a developer to use pyarmor is

* Generate project capsule for each project
* Encrypt python scripts with project capsule
* Distribute the encrypted scripts to target machine

Next it's an example to show you how to use pyarmor to encrypt scripts
and how to distribute encrypted scripts.

Encrypt Script
--------------

Assume you have 2 scripts: moda.py modb.py,

* Generate project capsule

  `For example,`::

    $ python pyarmor.py capsule

  It will make a file "project.zip" in the current directory.

* Encrypt python scripts

  `For example,`::

    $ python pyarmor.py encrypt --with-capsule=project.zip \
      moda.py modb.py

  After above command finished, you will find the following files in
  the path "dist"

    * moda.pyx
    * modb.pyx

    * pyimcore.py
    * pytransform.pyd (for windows) or pytransform.so (for linux)
    * cygtfm-0.dll / libtfm-0.dll (only for windows)
    * cygtomcrypt-0.dll / libtomcrypt-0.dll (only for windows)
    * pyshield.key
    * pyshield.lic
    * product.key
    * license.lic

  The first 2 files are encrypted scripts, the others are
  auxiliary. All of these files is required when distribute encrypted
  scripts.

  `About more usage of pyarmor`::

     C:/Python32/python pyarmor --help
     C:/Python32/python pyarmor encrypt --help

Distribute Script
-----------------

Before you distribute encrypted scripts above, you need change a
little in your main script -- add a line 'import pyimcore' before
import those encrypted module. Assume your startup script is main.py,
what you will do is add a line in the file header somewhere.

`For example,`::

  import pyimore

The main function of pyimcore is to install an import hook, so that
the encrypted module will be imported correctly. For you, everything
is transparent, all of the source code need to be changed nothing
else !

Now copy the following files to your customer:

  * main.py
  * moda.pyx
  * modb.pyx

  * pyimcore.py
  * pytransform.pyd (for windows) or pytransform.so (for linux)
  * cygtfm-0.dll / libtfm-0.dll (only for windows)
  * cygtomcrypt-0.dll / libtomcrypt-0.dll (only for windows)
  * pyshield.key
  * pyshield.lic
  * product.key
  * license.lic

And run it as if there are no any encrypted scripts.

Generate Special "license.lic"
------------------------------

By default, the distribute path will include a file "license.lic",
it's required to run/import encrypted scripts. You can generate other
license file by command "license" for special users.

`Generate license.lic with registration code "MYPROJECT-001"`::

  $ python pyarmor.py license --with-capsule=project.zip MYPROJECT-001

This command will generate a new "license.lic" with registration code
"MYPROJECT-001", replace the old with this one in "dist" path.

Advanced Usage
==============

Run Encrypted Script
--------------------

Someone maybe say I want to encrypt my startup script either, then how
to run it.

`Encrypt the script at first,`::

    $ python pyarmor.py encrypt --with-capsule=project.zip \
      main.py moda.py modb.py

`Run python with -c, for example,`::

    python -c "import pyimcore
    import pytransform
    pytransform.exec_file('main.pyx')"

`Or create a startup script startup.py like this,`::

    import pyimcore
    import pytransform
    pytransform.exec_file('main.pyx')

Then run startup.py as normal python script.

You can read the source file pyarmor.py to know the basic usage of
pytransform extension.

Cross Publish
-------------

If target machine is different from development machine, you need use
option '--with-extension' to publish encrypted scripts. A common case
is to distribute python scripts to embedded linux system. The only
difference is to replace python extension "pytransform" with the
corresponding platform.

In the sub-directory "extensions" of pyarmor, there are many files
looks like:

    pytransform-1.7.2.win32-ARCH-pyX.Y.pyd
    pytransform-1.7.2.linux-ARCH-pyX.Y.so

X.Y is python major and minor version, ARCH may be x86, x86_64, arm etc.

`Encrypt scripts with option --with-extension`::
  
    $ python pyarmor.py encrypt --with-capsule=project.zip \
      --with-extension=extensions/pytransform-1.7.2.linux-arm-py2.so \
      main.py moda.py modb.py
  
`Another example, encrypted scripts for Python2.3`::
  
    $ python3  pyarmor.py encrypt --with-capsule=project.zip \
      --with-extension=extensions/pytransform-1.7.2.win32-x86-py2.3.pyd \
      main.py moda.py modb.py
  

Generate "license.lic" For Special Machine
------------------------------------------

Sometimes you want to run/import encrypted scripts in special
machine. You can generate a "license.lic" bind to serial number of
hard disk.

`Generate license.lic with serial number of hard disk "PBN2081SF3NJ5T"`::

    $ python pyarmor.py license --with-capsule=project.zip --bind \
      PBN2081SF3NJ5T

This command will generate a new "license.lic" bind to harddisk which
serial number is "PBN2081SF3NJ5T", replace the old with this one in
"dist" path.

Generate Periodic "license.lic"
-------------------------------

`Generate license.lic which will be expired in Jan. 31, 2015`::

    $ python pyarmor.py license --with-capsule=project.zip --expired-date \
      2015-01-31

This command will generate a new "license.lic" will be expired in
Jan. 31, 2015.

Change Logs
===========

2.3.2
-----
* Fix error data in examples of wizard

2.3.1
-----
* Implement Run function in the GUI wizard
* Make license works in trial version

2.2.1
-----
* Add a GUI wizard
* Add examples to show how to use pyarmor

2.1.2
-----
* Fix syntax-error when run/import encrypted scripts in linux x86_64

2.1.1
-----
* Support armv6

2.0.1
-----
* Add option '--path' for command 'encrypt'
* Support script list in the file for command 'encrypt'
* Fix issue to encrypt an empty file result in pytransform crash

1.7.7
-----

* Add option '--expired-date' for command 'license'
* Fix undefined 'tfm_desc' for arm-linux
* Enhance security level of scripts

1.7.6
-----

* Print exactaly message when pyarmor couldn't load extension
  "pytransform"

* Fix problem "version 'GLIBC_2.14' not found"

* Generate "license.lic" which could be bind to fixed machine.

1.7.5
-----

* Add missing extensions for linux x86_64.

1.7.4
-----

* Add command "licene" to generate more "license.lic" by project
  capsule.

1.7.3
-----

* Add information for using registration code

1.7.2
-----

* Add option --with-extension to support cross-platform publish.
* Implement command "capsule" and add option --with-capsule so that we
  can encrypt scripts with same capsule.
* Remove command "convert" and option "-K/--key"

1.7.1
-----

* Encrypt pyshield.lic when distributing source code.

1.7.0
-----

* Enhance encrypt algorithm to protect source code.
* Developer can use custom key/iv to encrypt source code
* Compiled scripts (.pyc, .pyo) could be encrypted by pyshield
* Extension modules (.dll, .so, .pyd) could be encrypted by pyshield

FAQ
===

Q: Will the license expire? Is the license the same for develop machine
and target machine?

A::

  "license.lic" for pyarmor will expired about by the end of next
   month.  After that, a registration code is required to run pyarmor.

   The "license.lic" in the target machine is different from develop
   machine, it is generated by pyarmor. Simply to say, "license.lic"
   of pyarmor is generated by me, "license.lic" in the target machine
   is generated by developer who uses pyarmor.

Q: If I pay for the registration code, it is valid forever? Or I have to
pay periodically?

A::

  Forever now.

Known Issues
============

[Need document]

Bug reports
===========

Send an email to: ``jondy.zhao@gmail.com``, Thanks.

More Information
================

The trial license will be expired in the end of this quarter, after
that, you need pay for registration code from

  http://dashingsoft.com/products/pyarmor.html

You will receive information electronically immediately after
ordering, then replace the content of "license.lic" with registration
code only (no newline).

Copyright (c) 2009 - 2015 Dashingsoft Corp. All rights reserved.

2015-03-05 10:48 + China Standard Time
