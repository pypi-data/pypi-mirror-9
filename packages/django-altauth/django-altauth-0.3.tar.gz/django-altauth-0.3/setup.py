#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'django-altauth',
          version = '0.3',
          description = '''''',
          long_description = '''A Django appliaction to allow for alternative login methods, mainly focused on authentication from static scripts''',
          author = "Mirko Rossini",
          author_email = "mirko.rossini@ymail.com",
          license = '',
          url = 'https://github.com/MirkoRossini/django-altauth',
          scripts = [],
          packages = ['altauth', 'altauth.utils'],
          py_modules = ['manage'],
          classifiers = ['Environment :: Web Environment', 'Framework :: Django', 'Intended Audience :: Developers', 'License :: OSI Approved :: BSD License', 'Operating System :: OS Independent', 'Programming Language :: Python', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Topic :: Internet :: WWW/HTTP', 'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
          package_data = {'altauth': ['templates/altauth/*', 'templates/base.html']},   # package data
          install_requires = [ "rsa>=3.1.2" ],
          
          zip_safe=True
    )
