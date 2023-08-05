# coding: utf-8
from setuptools import setup
import lua_table
import os.path


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as inf:
        return "\n" + inf.read().replace("\r\n", "\n")

setup(
    name='lua_table',
    version=lua_table.__version__,
    description='Parser of the serialized Lua tables',
    author='Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='https://gitlab.com/mcepl/lua_table/',
    py_modules=['lua_table'],
    long_description=read("README.rst"),
    keywords=['Lua'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="test",
    install_requires=['rply']
)
