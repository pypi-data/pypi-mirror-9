# -*- coding: latin-1 -*-

#!/usr/bin/env python

from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(name='textmodel',
      version='0.3.1',
      description = \
          'A data type holding rich text data (textmodel) '\
          'and a text widget (wxtextview) as demonstration. '\
          'Textmodel does not depend on a specific gui-toolkit.',
      long_description = long_description,
      author='C. Ecker',
      author_email='textmodelview@gmail.com',
      url='https://pypi.python.org/pypi/textmodel/',
      license='See file LICENSE',
      packages=['textmodel', 'wxtextview'],
      platforms = ['any'],
     )

