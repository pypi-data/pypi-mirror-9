#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 - 2014 Dashingsoft corp.            #
#      All rights reserved.                                 #
#                                                           #
#      Pyshield                                             #
#                                                           #
#      Version: 1.7.0 - 2.1.1                               #
#                                                           #
#############################################################
#
#
#  @File: pyarmor.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2013/07/24
#
#  @Description:
#
#   Command line tool of pytransform, used to run/import the
#   encrypted python scripts.
#
import fnmatch
import getopt
import gettext
import glob
import logging
import os
import platform
import shutil
import sys
import tempfile
import time
from zipfile import ZipFile
try:
    from functools import reduce
except Exception:
    pass

try:
    unhexlify = bytes.fromhex
except Exception:
    from binascii import a2b_hex as unhexlify

__version__ = '2.1.1'
__versioninfo__ = '''
Pyarmor {0}
Copyright (c) 2009 - 2014 Dashingsoft Corp. All rights reserved.

Pyarmor is a program used to run the encrypted python scripts under
Windows and Linux. Its main advantages over similar tools are that
Pyarmor is only encrypt the script and the whole package structures
will not be changed.

Contact: Jondy Zhao (jondy.zhao@gmail.com)
Support URL: http://dashingsoft.com/products/pyarmor.html

'''.format(__version__)

__helpfooter__ = '''
Report bugs by sending email to <jondy.zhao@gmail.com>.
'''

__errormsg__ = '''
The trial license is expired, you need pay for a registration code
from:

  http://dashingsoft.com/products/pyarmor.html

You will receive information electronically immediately after ordering,
then replace "license.lic" with registration code only (no newline).
'''

def import_pytransform():
    try:
        logging.info('loading pytransform ...')
        m = __import__('pytransform')
        logging.info('loading pytransform OK.')
        return m
    except ImportError:
        pass

    target, src = format_extension_filename()
    if src is None:
        raise RuntimeError('Missing extension files')
    if os.path.exists(target):
        logging.info('remove old pytransform extension "%s"' % target)
        os.remove(target)
    assert os.path.exists(src)
    logging.info('find pytransform extension "%s"' % src)
    logging.info('copy %s to %s' % (src, target))
    shutil.copyfile(src, target)
    for filename in get_related_files(src):
        if os.path.exists(filename):
            shutil.copy(filename, sys.rootdir)
        else:
            logging.info('missing file "%s"' % filename)
            raise RuntimeError('missing file "%s"' % filename)
    try:
        m = __import__('pytransform')
        logging.info('Load pytransform OK.')
        return m
    except ImportError as e:
        if str(e).startswith('Invalid license.'):
            pass
        else:
            raise

    logging.info('no pytransform extension found, use PseudoTransform()')
    class PseudoTransform:
        __file__ = ''
        def error_msg(self, *args):
            sys.stderr.write(__errormsg__)
            sys.exit(1)
        encrypt_files = error_msg
        encrypt_project_files = error_msg
        generate_project_capsule = error_msg
        generate_module_key = error_msg
        encode_license_file = error_msg
    m = PseudoTransform()
    m.error_msg()
    return m

def print_version_info():
    print(__versioninfo__)

def usage(command=None):
    if command:

        if 'version'.startswith(command):
            print(_('''
Usage: pyarmor version

  Show the version information, or you can type
      pyarmor -v
      pyarmor --version
  These forms are same to show the version information.
'''))

        elif 'encrypt'.startswith(command):
            print(_('''
Usage: pyarmor encrypt [OPTIONS] [File Patterns or @Filename]

  Encrpty the files list in the command line, you can use a
  specified pattern according to the rules used by the Unix
  shell. No tilde expansion is done, but *, ?, and character
  ranges expressed with [] will be correctly matched.

  You can either list file patterns in one file, one pattern one line,
  then add a prefix '@' to the filename.

  All the files will be encrypted and saved as orginal file
  name plus 'x'. By default, the encrypted scripts and all the
  auxiliary files used to run the encrypted scripts are save in
  the path "dist".

  Available options:

  -O, --output=DIR                [option], all the encrypted files will
                                  be saved here.
                                  The default value is "dist".

  -C, --with-capsule=FILENAME     [option] Specify the filename of capsule
                                  generated before. If this option isn't
                                  specified, pyarmor will generate a
                                  temporary capsule to encrypt the scripts.

  -P, --path=DIR                  [option], the source path of python scripts.
                                  The default value is current path.

                                  The default value is "dist".
  -S, --with-extension=FILENAME   [option] Specify the filename of python
                                  module "pytransform", only used for cross
                                  publish. By default, it will be the value
                                  of pytransform.__file__ imported by pyarmor.

  For examples:

    - Encrypt a.py and b.py as a.pyx and b.pyx, saved in the path "dist":

      pyarmor encrypt a.py b.py

    - Use file pattern to specify files:

      pyarmor encrypt a.py *.py src/*.py lib/*.pyc

    - Save encrypted files in the directory "/tmp/build" other than "dist":

      pyarmor encrypt --output=/tmp/build a.py

    - Encrypt python scripts by project capsule "project.zip" in the
      current directory:

      pyarmor encrypt --with-capsule=project.zip src/*.py

    - Encrypt python scripts to run in different platform:

      pyarmor encrypt \
        --with-extension=extensions/pytransform-1.7.2.linux-armv7.so \
        a.py b.py

'''))

        elif 'capsule'.startswith(command):
            print(_('''
Usage: pyarmor capsule [Options] [name]

  Generate a capsule which used to encrypt/decrypt python scripts later, it
  will generate different capsule when run this command again. Generately,
  one project, one capsule.

  Available options:

  -O, --output=DIR            [option] The path used to save capsule file.

  For example,

     - Generate default capsule "project.zip":

       pyarmor capsule

     - Generate a capsule "dist/foo.zip":

       pyarmor capsule --output=dist foo
'''))

        elif 'license'.startswith(command):
            print(_('''
Usage: pyarmor license [Options] [CODE]

  Generate a registration code for project capsule, save it to "license.lic"
  by default.

  Available options:

  -O, --output=DIR                [option] The path used to save license file.

  -B, --bind                      [option] Generate license file bind to fixed machine.

  -e, --expired-date=YYYY-MM-NN   [option] Generate license file expired in certain day.
                                           This option could be combined with "--bind"

  -C, --with-capsule=FILENAME     [required] Specify the filename of capsule
                                  generated before.

  For example,

     - Generate a license file "license.lic" for project capsule "project.zip":

       pyarmor license --wth-capsule=project.zip MYPROJECT-0001

     - Generate a license file "license.lic" expired in 05/30/2015:

       pyarmor license --wth-capsule=project.zip -e 2015-05-30 MYPROJECT-0001

     - Generate a license file "license.lic" bind to machine whose harddisk's
       serial number is "PBN2081SF3NJ5T":

       pyarmor license --wth-capsule=project.zip --bind PBN2081SF3NJ5T

'''))

        else:
            print(_('unknown command "%s"') % command)
            usage()
            return

    else:
        print(_('''
Usage: pyarmor [command name] [options]

  command name can be one of the following list

    help                show the usage
    version             show the version information
    encrypt             encrypt the scripts
    capsule             generate all the files used to
                        run the encrypted scripts
    license             generate registration code

  if you want to know the usage of each command, type the
  following command:

    pyarmor help [command name]

  and you can type the left match command, such as

     pyarmor c
  or pyarmor cap
  or pyarmor capsule

  all of these forms are same.
'''))

    # show this for each command except the unknown command
    print(__helpfooter__)

def format_arch():
    arch = platform.machine().lower()
    if arch in ('amd64', 'x86_64'):
        arch = 'x86_64'
    elif arch in ('x86', 'i386', 'i486', 'i586', 'i686'):
        arch = 'x86'
    elif arch.startswith('arm'):
        arch = 'arm'
    else:
        raise RuntimeError('Unsupport processor architecture.')
    return arch

def format_extension_filename():
    ''' Get standard pytransform name by arch and os

    pytransform-X.Y.Z.win32-x86-pyM.N.pyd
    pytransform-X.Y.Z.win32-x86_64-pyM.N.pyd

    pytransform-X.Y.Z.linux-x86-pyM.N.so
    pytransform-X.Y.Z.linux-x86_64-pyM.N.so
    pytransform-X.Y.Z.linux-arm-pyM.N.so

    '''
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if major < 3 and minor < 6:
        raise RuntimeError('Pyarmor need python 2.6 or later')

    if sys.platform.startswith('linux'):
        ext = 'so'
        osname = 'linux'
    elif sys.platform.startswith('win'):
        ext = 'pyd'
        osname = 'win32'
    else:
        raise RuntimeError('This platform is unsupported.')

    arch = format_arch()
    target = os.path.join(sys.rootdir, 'pytransform.%s' % ext)
    pyver = '%i.%i' % (major, minor)
    pat = os.path.join(
        sys.rootdir,
        'extensions',
        'pytransform-*.%s-%s-py%s.%s' % (osname, arch, pyver, ext)
        )
    src = None
    ct = None
    for s in glob.glob(pat):
        _ct = os.path.getctime(s)
        if ct is None or _ct < ct:
            src = s
            ct = _ct
    return target, src

def get_related_files(extfilename=None):
    # Native publish
    if extfilename is None:
        osname = sys.platform
        arch = format_arch()
        path = os.path.dirname(pytransform.__file__)
    # Cross publish
    else:
        fs = os.path.basename(extfilename).split('-')
        osname = fs[1].rsplit('.', 1)[-1]
        arch = fs[2]
        path = os.path.dirname(extfilename)
    if osname == 'win32':
        if arch == 'x86':
            filelist = 'cygtfm-0.dll', 'cygtomcrypt-0.dll'
        else:
            filelist = 'libtfm-0.dll', 'libtomcrypt-0.dll', 'libgcc_s_seh-1.dll'
    else:
        filelist = []
    return [os.path.join(path, s) for s in filelist]

def make_capsule(rootdir=None, keystr=None, filename='project.zip'):
    '''Generate all the files used by running encrypted scripts, pack all
    of them to a zip file.

    rootdir        pyarmor root dir, where you can find license files,
                   auxiliary library and pyshield extension module.

    keystr         32 bytes hex-string as encrypt key.

    filename       output filename, the default value is project.zip

    Return True if sucess, otherwise False or raise exception
    '''
    try:
        if rootdir is None:
            rootdir = sys.rootdir
    except AttributeError:
        rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    filelist = 'public.key', 'pyimcore.py'
    for x in filelist:
        src = os.path.join(rootdir, x)
        if not os.path.exists(src):
            logging.error(_('missing %s') % src)
            return False

    licfile = os.path.join(rootdir, 'license.lic')
    if not os.path.exists(licfile):
        logging.error(_('missing license file %s') % licfile)
        return False

    logging.info(_('generate product key'))
    pri, pubx, lic = pytransform.generate_project_capsule()

    logging.info(_('generating capsule %s ...') % filename)
    myzip = ZipFile(filename, 'w')
    try:
        myzip.write(os.path.join(rootdir, 'public.key'), 'pyshield.key')
        myzip.writestr('pyshield.lic', pytransform.encode_license_file(licfile))
        myzip.write(os.path.join(rootdir, 'pyimcore.py'), 'pyimcore.py')
        myzip.writestr('private.key', pri)
        myzip.writestr('product.key', pubx)
        myzip.writestr('license.lic', lic)
        if keystr is not None:
            myzip.writestr(
                'module.key',
                pytransform.generate_module_key(pubx, unhexlify(keystr.replace(' ', '')))
                )
            myzip.writestr('key.txt', ''.join(format_kv(keystr)))
    finally:
        myzip.close()
    logging.info(_('generate capsule %s OK.') % os.path.abspath(filename))
    return True

def encrypt_files(files, kv, output=None):
    '''Encrypt all the files, all the encrypted scripts will be plused with
    a suffix 'x', for example, hello.py -> hello.pyx

    files          list all the scripts
    kv             32 bytes used to encrypt scripts
    output         output directory. If None, the output file will be saved
                    in the same path as the original script

    Return None if sucess, otherwise raise exception
    '''
    if output is None:
        fn = lambda a, b : b + 'x'
    else:
        fn = lambda a, b : os.path.join(a, os.path.basename(b) + 'x')
        if not os.path.exists(output):
            os.makedirs(output)

    flist = []
    for x in files:
        flist.append((x, fn(output, x)))
        logging.info(_('encrypt %s to %s') % flist[-1])

    if flist[:1]:
        if isinstance(kv, str) and kv.endswith('product.key'):
            if not os.path.exists(kv):
                raise RuntimeError('missing product.key')
            pytransform.encrypt_project_files(kv, tuple(flist))
        else:
            pytransform.encrypt_files(kv, tuple(flist))
        logging.info(_('encrypt all scripts OK.'))
    else:
        logging.info(_('No script found.'))

def make_license(capsule, filename, fmt):
    myzip = ZipFile(capsule, 'r')
    myzip.extract('private.key', tempfile.gettempdir())
    prikey = os.path.join(tempfile.tempdir, 'private.key')
    start = -1
    count = 1
    pytransform.generate_serial_number(filename, prikey, fmt, start, count)
    os.remove(prikey)

def get_kv(value):
    if os.path.exists(value):
        f = open(value, 'r')
        value = f.read()
        f.close()
    return value.replace('\n', ' ').replace('\r', '')

def format_kv(keystr):
    counter = 0
    for c in keystr:
        if c in '0123456789abcdefABCEDF':
            counter += 1
            if counter % 16 == 0:
                yield h + c + '\n'
            elif counter % 2 == 0:
                yield h + c + ' '
            else:
                h = c

def do_encrypt(argv):
    try:
        opts, args = getopt.getopt(
            argv,
            'C:O:P:S:',
            ['output=', 'path=', 'with-capsule=', 'with-extension=']
            )
    except getopt.GetoptError:
        logging.exception('option error')
        usage('encrypt')
        sys.exit(1)

    if len(args) == 0:
        logging.error(_('missing the script names'))
        usage('encrypt')
        sys.exit(2)

    output = 'dist'
    srcpath = None
    kv = None
    capsule = None
    extfile = None

    for o, a in opts:
        if o in ('-O', '--output'):
            output = a
        elif o in ('-P', '--path'):
            srcpath = a
        elif o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-S', '--with-extension'):
            extfile = a

    if srcpath is not None and not os.path.exists(srcpath):
        logging.error(_('missing base path "%s"') % srcpath)
        return False

    if capsule is not None and not os.path.exists(capsule):
        logging.error(_('missing capsule file'))
        return False

    if output == '':
        output = os.getcwd()

    logging.info(_('output path is %s') % output)
    if not os.path.exists(output):
        logging.info(_('make output path: %s') % output)
        os.makedirs(output)

    if extfile is None:
        extfile = pytransform.__file__
        relfiles = get_related_files()
    elif os.path.exists(extfile):
        relfiles = get_related_files(extfile)
    else:
        logging.error(_('missing pytransform extension file %s') % extfile)
        return False

    if extfile.endswith('.pyd'):
        target = os.path.join(output, 'pytransform.pyd')
    elif extfile.endswith('.so'):
        target = os.path.join(output, 'pytransform.so')
    else:
        raise RuntimeError(_('Unsupport extension format'))

    logging.info(_('copy %s as %s') % (extfile, target))
    shutil.copy(extfile, target)

    for filename in relfiles:
        if not os.path.exists(filename):
            logging.error(_('missing file %s') % filename)
            return False
        logging.info(_('copy %s to %s') % (filename, output))
        target = os.path.join(output, os.path.basename(filename))
        shutil.copy(filename, target)

    if kv is not None:
        logging.info(_('key is %s') % kv)

    filelist = []
    patterns = []
    for arg in args:
        if arg[0] == '@':
            f = open(arg[1:], 'r')
            for pattern in f.read().splitlines():
                if not pattern.strip() == '':
                    patterns.append(pattern.strip())
            f.close()
        else:
            patterns.append(arg)
    for pat in patterns:
        if os.path.isabs(pat) or srcpath is None:
            for name in glob.glob(pat):
                filelist.append(name)
        else:
            for name in glob.glob(os.path.join(srcpath, pat)):
                filelist.append(name)

    if capsule is None:
        logging.info(_('make anonymous capsule'))
        filename = os.path.join(output, 'tmp_project.zip')
        make_capsule(sys.rootdir, None, filename)
        logging.info(_('extract anonymous capsule'))
        ZipFile(filename).extractall(path=output)
        os.remove(filename)
    else:
        logging.info(_('extract capsule %s') % capsule)
        ZipFile(capsule).extractall(path=output)
    prikey = os.path.join(output, 'private.key')
    if os.path.exists(prikey):
        logging.info(_('remove private key %s') % capsule)
        os.remove(prikey)
    kvfile = os.path.join(output, 'key.txt')
    if os.path.exists(kvfile):
        logging.info(_('use capsule key in %s') % kvfile)
        kv = unhexlify(get_kv(kvfile).replace(' ', ''))
        logging.info(_('remove key file %s') % kvfile)
        os.remove(kvfile)

    if kv is None:
        kv = os.path.join(output, 'product.key')
    elif not os.path.exists(os.path.join(output, 'module.key')):
        raise RuntimeError(_('missing module key'))
    logging.info(_('encrypt files ...'))
    encrypt_files(filelist, kv, output)

    logging.info(_('Encrypt files OK.'))

def do_capsule(argv):
    try:
        opts, args = getopt.getopt(argv, 'K:O:', ['key=', 'output='])
    except getopt.GetoptError:
        logging.exception('option error')
        usage('capsule')
        sys.exit(2)

    output = ''
    keystr = None
    for o, a in opts:
        if o in ('-K', '--key'):
            keystr = get_kv(a)
        elif o in ('-O', '--output'):
            output = a

    if output == '':
        output = os.getcwd()

    if not os.path.exists(output):
        logging.info(_('make output path: %s') % output)
        os.makedirs(output)

    if len(args) == 0:
        filename = os.path.join(output, 'project.zip')
    else:
        filename = os.path.join(output, '%s.zip' % args[0])

    if keystr is not None:
        logging.info(_('key is %s') % keystr)
    logging.info(_('output filename is %s') % filename)
    make_capsule(sys.rootdir, keystr, filename)
    logging.info(_('Generate capsule OK.'))

def do_license(argv):
    try:
        opts, args = getopt.getopt(
            argv,
            'BC:e:O:',
            ['bind', 'expired-date=', 'with-capsule=', 'output=']
            )
    except getopt.GetoptError:
        logging.exception('option error')
        usage('license')
        sys.exit(2)

    filename = 'license.lic'
    capsule = 'project.zip'
    bindflag = False
    expired = None
    for o, a in opts:
        if o in ('-C', '--with-capsule'):
            capsule = a
        elif o in ('-B', '--bind'):
            bindflag = True
        elif o in ('-e', '--expired-date'):
            expired = a
        elif o in ('-O', '--output'):
            if os.path.exists(a) and os.path.isdir(a):
                filename = os.path.join(a, 'license.lic')
            else:
                filename = a

    if len(args) == 0:
        fmt = 'PROJECT-CODE'
    else:
        fmt = args[0]
    if bindflag:
        fmt = '*HARDDISK:%s' % fmt
    if expired is not None:
        fmt = '*TIME:%.0f\n%s' % (
            time.mktime(time.strptime(expired, '%Y-%m-%d')), fmt
            )

    logging.info(_('output filename is %s') % filename)
    make_license(capsule, filename, fmt)
    logging.info(_('Generate license file "%s" OK.') % filename)

if __name__ == '__main__':
    sys.rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)-8s %(message)s',
            # filename=os.path.join(sys.rootdir, 'pyarmor.log'),
            # filemode='w',
            )
    except TypeError:
        # Only for Python 2.3
        logging.basicConfig()

    try:
        lang = gettext.translation('pyarmor')
    except IOError:
        lang = gettext.NullTranslations()
    lang.install()

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    else:
        pytransform = import_pytransform()
        command = sys.argv[1]
        if len(sys.argv) >= 3 and sys.argv[2] == 'help':
            usage(command)
            sys.exit(0)

        if ('help'.startswith(command)
            or sys.argv[1] == '-h'
            or sys.argv[1] == '--help'
            ):
            try:
                usage(sys.argv[2])
            except IndexError:
                usage()

        elif ('version'.startswith(command)
              or sys.argv[1] == '-v'
              or sys.argv[1] == '--version'
              ):
            print_version_info()

        elif 'encrypt'.startswith(command):
            do_encrypt(sys.argv[2:])

        elif 'capsule'.startswith(command):
            do_capsule(sys.argv[2:])

        elif 'license'.startswith(command):
            do_license(sys.argv[2:])

        else:
            usage(command)
