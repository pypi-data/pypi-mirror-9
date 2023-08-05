#!/usr/bin/env python

from distutils.core import setup
import genpass

setup(name='genpass',
      version=genpass.__version__,
      description='Memorable Passphrase Generator',
      author='Steven Dee',
      author_email='steve@smartercode.net',
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Security',
          'Topic :: Utilities',
      ],
      license='MIT',
      py_modules=['genpass'],
      scripts=['genpass'])
