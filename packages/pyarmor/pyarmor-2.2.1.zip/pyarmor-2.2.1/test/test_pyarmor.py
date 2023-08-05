# -*- coding: utf-8 -*-
#
import gettext
import logging
import os
import shutil
import sys
import tarfile
import tempfile

if sys.version_info[0] == 2:
    from test import test_support as test_support
else:
    import test.support as test_support
import unittest

__src_path__ = r"d:\projects\pyarmor"

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.work_path = tempfile.mkdtemp()

        self.key = '\x01\x02\x03\x04\x05\x06\x07\x00' \
                   '\x01\x02\x03\x04\x05\x06\x07\x00' \
                   '\x01\x02\x03\x04\x05\x06\x07\x00'
        self.iv = '\x01\x02\x03\x00\x00\x03\x02\x01'
        self.keystr = '00 01 02 03 04 05 06 07\n' \
                      '08 09 0A 0B 0C 0D 0E 0F\n' \
                      '10 11 12 13 14 15 16 17\n' \
                      '18 19 1A 1B 1C 1D 1E 1F\n'
        tar = tarfile.open(os.path.join('data', 'sample.tar.gz'))
        tar.extractall(path=self.work_path)
        tar.close()

        self.pyarmor = test_support.import_module('pyarmor')
        self.pyarmor.pytransform = test_support.import_module('pytransform')

    def tearDown(self):
        shutil.rmtree(self.work_path)

class PyarmorTestCases(BaseTestCase):

    def test_make_capsule(self):
        ft = self.pyarmor.make_capsule
        filename = os.path.join(self.work_path, 'pycapsule.zip')
        ft(rootdir=__src_path__, filename=filename)
        self.assertTrue(os.path.exists(filename))

    def test_format_kv(self):
        key = self.keystr
        ft = self.pyarmor.format_kv
        self.assertEquals(''.join(list(ft(key))), key)

    def test_make_capsule_with_key(self):
        ft = self.pyarmor.make_capsule
        filename = os.path.join(self.work_path, 'pycapsule.zip')
        keystr = self.keystr.replace('\n', ' ')
        ft(rootdir=__src_path__, keystr=keystr, filename=filename)
        self.assertTrue(os.path.exists(filename))

    def test_do_capsule_with_key(self):
        ft = self.pyarmor.do_capsule

        key = self.keystr
        output = os.path.join(self.work_path, 'build')
        argv = ['-K', key, '-O', output, 'project_key']
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'project_key.zip')))

    def test_encrypt_files(self):
        ft = self.pyarmor.encrypt_files
        files = [os.path.join(self.work_path, 'examples', 'hello1.py')]
        kv = self.key + self.iv
        ft(files, kv)
        self.assertTrue(os.path.exists(files[0] + 'x'))

    def test_encrypt_files_with_output(self):
        ft = self.pyarmor.encrypt_files
        files = [os.path.join(self.work_path, 'examples', 'hello1.py')]
        kv = self.key + self.iv
        output = os.path.join(self.work_path, 'build')
        ft(files, kv, output=output)
        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.pyx')))

    def test_do_encrypt(self):
        ft = self.pyarmor.do_encrypt

        output = os.path.join(self.work_path, 'build')
        argv = ['-O', output,
                os.path.join(self.work_path, 'examples/hello1.py'),
                os.path.join(self.work_path, 'examples/hello2.py'),
                os.path.join(self.work_path, 'examples/helloext.c'),
                os.path.join(self.work_path, 'examples/helloext.pyd'),
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'hello2.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.cx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pydx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    def test_do_encrypt_pattern_file(self):
        ft = self.pyarmor.do_encrypt

        output = os.path.join(self.work_path, 'build')
        argv = ['-O', output,
                os.path.join(self.work_path, 'examples/*.py'),
                ]
        ft(argv)

        self.assertTrue(os.path.exists(os.path.join(output, 'hello1.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'hello2.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyhello.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.key')))

    def test_do_encrypt_with_path(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(self.work_path, 'build')
        argv = ['-O', output, '--path',
                os.path.join(self.work_path, 'examples'),
                '*.pyd'
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'helloext.pydx')))

    def test_do_encrypt_empty_file(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(self.work_path, 'build')
        filename = os.path.join(self.work_path, 'examples', 'empty.py')
        f = open(filename, 'w')
        f.close()
        argv = ['-O', output, filename]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'empty.pyx')))

    def test_do_encrypt_with_path_at_file(self):
        ft = self.pyarmor.do_encrypt
        output = os.path.join(self.work_path, 'build')
        filename = os.path.join(self.work_path, 'filelist.txt')
        f = open(filename, 'w')
        f.write('register.py\n\ncore/pyshield.py')
        f.close()
        argv = ['-O', output, '--path',
                os.path.join(self.work_path, 'examples', 'pydist'),
                '@' + filename
                ]
        ft(argv)
        self.assertTrue(os.path.exists(os.path.join(output, 'register.pyx')))
        self.assertTrue(os.path.exists(os.path.join(output, 'pyshield.pyx')))

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(message)s',
        filename=os.path.join(os.getcwd(), 'test_pyarmor.log'),
        filemode='w',
        )
    sys.path.insert(0, __src_path__)
    sys.rootdir = __src_path__
    if sys.platform == 'win32':
        src = os.path.join(
            __src_path__,
            'extensions',
            'pytransform-2.1.2.win32-x86-py%s.%s.pyd' % sys.version_info[:2]
            )
        shutil.copy(src, os.path.join(__src_path__, 'pytransform.pyd'))
    else:
        src = os.path.join(data_path, 'pytransform.so')
        shutil.copy(src, os.path.join(__src_path__, 'pytransform.so'))
    sys.pyshield_path = __src_path__.encode() if sys.version_info[0] == 3 else __src_path__
    gettext.NullTranslations().install()
    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_format_kv'
    suite = loader.loadTestsFromTestCase(PyarmorTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
