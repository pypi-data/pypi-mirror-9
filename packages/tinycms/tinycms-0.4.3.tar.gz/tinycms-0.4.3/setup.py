from setuptools import setup, find_packages
import sys, os

version = '0.4.3'

setup(name='tinycms',
      version=version,
      description="Simple CMS for django",
      classifiers=["Framework :: Django","License :: OSI Approved :: MIT License","Programming Language :: Python"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='ccat',
      author_email='',
      url='https://www.whiteblack-cat.info/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "django",
          "django-mptt"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
