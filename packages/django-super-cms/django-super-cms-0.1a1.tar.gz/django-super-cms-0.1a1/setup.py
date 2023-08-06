# -*- coding:utf-8 -*-
# PROJECT_NAME : mysite
# FILE_NAME    : 
# AUTHOR       : younger shen

from setuptools import setup, find_packages
import sys, os

version = '0.1a1'

setup(name='django-super-cms',
      version=version,
      description="a simple cms app for django , just for small site usage",
      long_description="""\
      a simple cms app for django , just for small site usage,
      the app suites small site and small bussiness.
      """,
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='django-super-cms, django, cms, django cms',
      author='younger shen',
      author_email='younger.x.shen@gmail.com',
      url='https://github.com/youngershen/django-super-cms',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'Django >= 1.7'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
