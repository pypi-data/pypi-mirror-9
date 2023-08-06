# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen

from setuptools import setup, find_packages
import sys, os

version = '0.1a1'

setup(name='django-flash-message',
      version=version,
      description="a simple message util for django",
      long_description="""\
      the purpose of this software is to make a more simple message util for django,
      just set the message in a request , then get a message in another request , the
      message is for single  use , so it called flash message.
      """,
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='django-flash-message, django, message',
      author='younger shen',
      author_email='younger.x.shen@gmail.com',
      url='https://github.com/youngershen/django-flash-message',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'Django >= 1.6'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
