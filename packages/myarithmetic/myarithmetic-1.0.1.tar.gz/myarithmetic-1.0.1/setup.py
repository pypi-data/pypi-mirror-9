from setuptools import setup, find_packages
import sys, os

version = '1.0.1'

setup(name='myarithmetic',
      version=version,
      description="myarithmetic",
      long_description="""\
(operand, +, -, *, /)""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='myarithmetic',
      author='coolsnow77',
      author_email='cuimingwen001@126.com',
      url='http://pypi.python.org/pypi/myarithmetic',
      license='Apache',
      py_modules = ['myarithmetic'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
