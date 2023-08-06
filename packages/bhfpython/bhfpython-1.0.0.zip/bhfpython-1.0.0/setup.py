from distutils.core import setup

setup(
    name         = 'bhfpython',
    version      = '1.0.0',
    py_modules   = ['bhfpython'],

    author       = 'csell',
    author_email = 'csell@outlook.com',
    url          = 'http://www.headfirstpython.com',
    description  = 'examples from the book'
    )
    
''' LOCAL
    python setup.py sdist
    python setup.py install
    PYPI
    python setup.py register
    python setup.py sdist upload'''
