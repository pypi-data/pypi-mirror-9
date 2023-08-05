# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2013 Dashingsoft corp.                   #
#      All rights reserved.                                 #
#                                                           #
#      Pyshield                                             #
#                                                           #
#      Version: 1.7.0 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyimcore.py
#
#  @Author: Jondy Zhao(jondy.zhao@gmail.com)
#
#  @Create Date: 2011/09/15
#
#  @Description:
#
#   Install an import hook for pyshield
#
import sys
import imp
import os
import site

try:
    import pytransform
except Exception:
    pass

class PyshieldImporter(object):

    def __init__(self):
        self.filename = ""

    def find_module(self, fullname, path=None):
        try:
            _name = fullname.rsplit('.', 1)[-1]
        except AttributeError:
            # no rsplit in Python 2.3
            _name = fullname.split('.', 1)[-1]
        if path is None:
            path = sys.path
        for dirname in path:
            self.filename = os.path.join(dirname, _name + '.pyx')
            if os.path.exists(self.filename):
                return self
            for ext in ('.pycx', '.pyox', '.pydx', '.sox'):
                self.filename = os.path.join(dirname, _name + ext)
                if os.path.exists(self.filename):
                    return self
        self.filename = ""

    def load_module(self, fullname):
        ispkg = 0
        try:
            mod = pytransform.import_module(fullname, self.filename)
            mod.__file__ = "<%s>" % self.__class__.__name__
            mod.__loader__ = self
        except Exception:
            raise ImportError("error occurred when import module")
        return mod

# install the hook
sys.meta_path.append(PyshieldImporter())
