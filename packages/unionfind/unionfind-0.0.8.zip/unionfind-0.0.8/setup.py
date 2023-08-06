from setuptools import setup

version = '0.0.8'
name = 'unionfind'
short_description = '`unionfind` is a package for unionfind.'
long_description = """\
`unionfind` is a package for unionfind.
::

   u = unionfind(3) # There are 3 items.
   u.unite(0, 2) # Set 0 and 2 to same group.
   u.issame(1, 2) # Ask "Are 1 and 2 same?"
   u.groups() # Return groups.

Requirements
------------
* Python 2 or Python 3

Features
--------
* nothing

Setup
-----
::

   $ easy_install unionfind

History
-------
0.0.1 (2015-4-3)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['unionfind'],
    keywords=['unionfind',],
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/unionfind',
    license='PSFL',
)