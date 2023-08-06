import sys
import re

if sys.version < '3.3':
    print('Sorry, this is not a compatible version of Python. Use 3.3 or later.')
    exit(1)

from setuptools import setup, find_packages

with open('README.rst') as f:
    description = f.read()

from circle_asset.version import VERSION, SHORT_DESCRIPTION

setup(name='circle-asset',
      version=VERSION,
      description=SHORT_DESCRIPTION,
      author='Alistair Lynn',
      author_email='arplynn@gmail.com',
      license="MIT",
      long_description=description,
      url='https://github.com/prophile/circle-asset',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Testing',
          'Topic :: System :: Installation/Setup'
      ],
      zip_safe=True,
      setup_requires=[
          'nose >=1, <2'
      ],
      install_requires=[
          'requests >=2.5, <3'
      ],
      tests_require=[
          'coverage >=3.7, <4'
      ],
      entry_points={'console_scripts': [
          'circle-asset=circle_asset.cli:main'
      ]},
      packages=find_packages())

