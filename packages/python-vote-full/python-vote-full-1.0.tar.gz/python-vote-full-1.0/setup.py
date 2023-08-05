import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
LICENSE = open(os.path.join(here, 'LICENSE.txt')).read()

setup(name='python-vote-full',
      version='1.0',
      description="Python based election methods, includes python-vote-core and python-graph-core.",
      long_description=README + '\n\n' + CHANGES + '\n\n' + LICENSE,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Scientific/Engineering :: Mathematics",
      ],
      author='Brad Beattie',
      author_email='bradbeattie@gmail com',
      url='https://github.com/bradbeattie/python-vote-core',
      license='GPLv3',
      keywords='library election',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[],
      tests_require=[],
      test_suite="test_functionality",
      )
