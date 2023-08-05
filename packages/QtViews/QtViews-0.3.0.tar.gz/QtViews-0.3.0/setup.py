# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import os
import sys
import distutils
from distutils.core import Command
from distutils.command.build import build

PY3 = sys.version > '3'

def needsupdate(src, targ):
    return not os.path.exists(targ) or os.path.getmtime(src) > os.path.getmtime(targ)

class PySideUiBuild:
    def qrc(self, qrc_file, py_file):
        import PySide
        qrc_compiler = os.path.join(PySide.__path__[0], 'pyside-rcc')
        import subprocess
        rccprocess = subprocess.Popen([qrc_compiler, qrc_file, '-py3' if PY3 else '-py2', '-o', py_file])
        rccprocess.wait()

    def uic(self, ui_file, py_file):
        import PySide
        uic_compiler = os.path.join(PySide.__path__[0], 'pyside-uic')
        import subprocess
        rccprocess = subprocess.Popen([uic_compiler, ui_file, '-o', py_file])
        rccprocess.wait()

class PyQt4UiBuild:
    def qrc(self, qrc_file, py_file):
        import subprocess
        rccprocess = subprocess.Popen(['pyrcc4', qrc_file, '-py3' if PY3 else '-py2', '-o', py_file])
        rccprocess.wait()

    def uic(self, ui_file, py_file):
        from PyQt4 import uic
        fp = open(py_file, 'w')
        uic.compileUi(ui_file, fp)
        fp.close()

class QtUiBuild(Command, PySideUiBuild):
    description = "build Python modules from Qt Designer .ui files"

    user_options = []
    ui_files = []
    qrc_files = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def compile_ui(self, ui_file, py_file):
        if not needsupdate(ui_file, py_file):
            return
        print("compiling %s -> %s" % (ui_file, py_file))
        try:
            self.uic(ui_file, py_file)
        except Exception as e:
            raise distutils.errors.DistutilsExecError('Unable to compile user interface %s' % str(e))
            return
    
    def compile_qrc(self, qrc_file, py_file):
        if not needsupdate(qrc_file, py_file):
            return
        print("compiling %s -> %s" % (qrc_file, py_file))
        try:
            self.qrc(qrc_file, py_file)
        except Exception as e:
            raise distutils.errors.DistutilsExecError('Unable to compile resource file %s' % str(e))
            return

    def run(self):
        for f in self.ui_files:
            dir, basename = os.path.split(f)
            self.compile_ui(f, os.path.join(dir, "ui_"+basename.replace(".ui", ".py")))
        for f in self.qrc_files:
            dir, basename = os.path.split(f)
            self.compile_qrc(f, os.path.join(dir, basename.replace(".qrc", "_rc.py")))

QtUiBuild.ui_files = []
QtUiBuild.qrc_files = [os.path.join(dir, f) \
                for dir in [] \
                for f in os.listdir(dir) if f.endswith('.qrc')]

class QtViewsBuild(build):
    sub_commands = [('build_ui', None)] + build.sub_commands

cmds = {
        'build' : QtViewsBuild,
        'build_ui' : QtUiBuild,
       }

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='QtViews',
    version='0.3.0', # also update in qtviews/__init__.py
    description='QtViews Library for Qt Helpers',
    author='Joel B. Mohler',
    author_email='joel@kiwistrawberry.us',
    license='LGPLv2+',
    long_description=read('README.txt'),
    url='https://bitbucket.org/jbmohler/qtviews/',
    cmdclass=cmds,
    packages=['qtviews'],
    scripts=[],
    install_requires=[], 
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent", 
        "Environment :: Win32 (MS Windows)", 
        "Environment :: X11 Applications :: Qt"])
