#!/usr/bin/env python 
import os

from distutils.core import setup


# lifted from Django REST Framework's setup.py
def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


# lifted from Django REST Framework's setup.py
def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
            for filename in filenames])

    return {package: filepaths}


setup(name='oauthclient',
      version='1.0.3',
      description='OAuth2 client library',
      author='Roberto Aguilar',
      author_email='roberto@sprocketlight.com',
      packages=get_packages('oauthclient'),
      package_data=get_package_data('oauthclient'),
      long_description=open('README.md').read(),
      url='http://github.com/rca/oauthclient',
      license='LICENSE',
)
