from distutils.cmd import Command
import os
import re
import sys
import shutil

from setuptools import setup


THIS_PATH = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))


def pkg_by_version(name=""):
    return name + ("" if sys.version_info[0] < 3 else "3")


def read(fname):
    with open(os.path.join(THIS_PATH, fname)) as f:
        return f.read()


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        self.paths = []

        for f in os.listdir(THIS_PATH):
            if re.search("(^(build|dist|__pycache__)$|\.egg-info)", f):
                self.paths.append(f)

        b = os.path.join(THIS_PATH, 'doc', 'build')

        for f in os.listdir(b):
            if b != 'html':
                self.paths.append(os.path.join(b, f))

        for root, dirs, files in os.walk(THIS_PATH):
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyc") or f.endswith(
                        ".pyo"):
                    self.paths.append(os.path.join(root, f))

            for f in dirs:
                if re.search("^(__pycache__)$", f):
                    self.paths.append(os.path.join(root, f))

    def finalize_options(self):
        pass

    def run(self):
        for p in self.paths:
            if os.path.exists(p):
                if os.path.isdir(p):
                    print("Remove directory: " + p)
                    shutil.rmtree(p)
                else:
                    print("Remove file     : " + p)
                    os.unlink(p)


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import doctest
        import tyuio

        failed, attemped = doctest.testmod(tyuio, report=True)

        if attemped:
            print("%s of %s tests passed!" % (attemped - failed, attemped))

        if failed:
            print("%s of %s tests failed!" % (failed, attemped))



setup(
    name="tyuio",
    version="0.3",
    author="Moises P. Sena",
    author_email="moisespsena@gmail.com",
    description=("Tyuio is a Simple Event Dispatcher api."),
    license="GPLv2",
    keywords="event dispatcher",
    url="https://github.com/moisespsena/py_tyuio",
    py_modules=['tyuio'],
    setup_requires=['sphinx'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={'clean': CleanCommand, 'test': TestCommand}
)
