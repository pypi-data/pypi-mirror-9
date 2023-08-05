#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='yt.recipe.relativeworkaround',
      version='0.0.2',
      description='A buildout recipe to add in shell commands',
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='http://github.com/toumorokoshi/yt.recipe.shell',
      packages=find_packages(),
      long_description=open('README').read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Build Tools',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],
      entry_points={
          'zc.buildout':
                    ['default = yt.recipe.relativeworkaround:RelativeWorkaround']
      }
)
