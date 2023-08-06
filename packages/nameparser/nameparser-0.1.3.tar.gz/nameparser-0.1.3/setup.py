from distutils.core import setup
import nameparser
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(name='nameparser',
      packages=['nameparser'],
      description = 'A simple Python module for parsing human names into their individual components.',
      long_description = README,
      version       = nameparser.__version__,
      url           = nameparser.__url__,
      author        = nameparser.__author__,
      author_email  = nameparser.__author_email__,
      license       = nameparser.__license__,
      classifiers = [
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          'Programming Language :: Python',
      ]
      )
