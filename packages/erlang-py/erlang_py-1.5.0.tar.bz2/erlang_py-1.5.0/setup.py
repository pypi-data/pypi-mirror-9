#-*-Mode:python;coding:utf-8;tab-width:4;c-basic-offset:4;indent-tabs-mode:()-*-
# ex: set ft=python fenc=utf-8 sts=4 ts=4 sw=4 et:
import setuptools
from distutils.core import setup, Command, Extension

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import tests.erlang_tests
        import unittest
        suite = unittest.TestSuite()
        suite.addTests(tests.erlang_tests.get_suite())
        unittest.TextTestRunner().run(suite)

setup(
    name='erlang_py',
    py_modules=['erlang'],
    cmdclass = {'test': PyTest},
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Erlang',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ],
    version='1.5.0',
    description='Erlang Binary Term Format for Python',
    author='Michael Truog',
    author_email='mjtruog@gmail.com',
    url='https://github.com/okeuday/erlang_py',
)
