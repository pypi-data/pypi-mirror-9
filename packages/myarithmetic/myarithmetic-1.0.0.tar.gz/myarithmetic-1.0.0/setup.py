from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

setup(name='myarithmetic',
      version=version,
      description="myarithmetic",
      long_description="""\
myarithmetic , arithmetic add, division, multiply, division""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='myarithmetic(operand + , - *, /)',
      author='cuimingwen001@126.com',
      author_email='cuimingwen001@126.com',
      url='http://pypi.python.org/myarithmetic',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
