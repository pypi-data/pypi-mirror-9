from distutils.core import setup

import os
import sys

# add the current directory as the first listing on the python path
# so that we import the correct version.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import version

setup(name='microdrop_utility',
      version=version.getVersion(),
      description='Utility functions and classes for MicroDrop, which might '
      'be potentially useful in other projects.',
      keywords='microdrop dropbot utility',
      author='Christian Fobel and Ryan Fobel',
      author_email='christian@fobel.net and ryan@fobel.net',
      url='http://github.com/cfobel/microdrop_utility.git',
      license='GPL',
      packages=['microdrop_utility', 'microdrop_utility.gui',
                'microdrop_utility.tests'],
      install_requires=['git_helpers'])
