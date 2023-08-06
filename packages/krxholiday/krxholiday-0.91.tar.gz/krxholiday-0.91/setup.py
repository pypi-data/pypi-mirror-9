
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'krxholiday',
    'author': 'shhong',
    'author_email': 'shhong@mirib.net',
    'version': '0.91',
    'install_requires': [],
    'packages': ['krxholiday'],
    'scripts': [],
    'name': 'krxholiday'
}

#http://www.scotttorborg.com/python-packaging/minimal.html
setup(**config)
