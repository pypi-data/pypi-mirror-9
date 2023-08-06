#!/usr/bin/env python

import os
import sys
import setuptools.command.egg_info as egg_info_cmd
import shutil

from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.rst')

try:
    import gittaggers
    tagger = gittaggers.EggInfoFromGit
except ImportError:
    tagger = egg_info_cmd.egg_info

setup(name='cwltool',
      version='1.0',
      description='Common workflow language reference implementation',
      long_description=open(README).read(),
      author='Common workflow language working group',
      author_email='common-workflow-language@googlegroups.com',
      url="https://github.com/common-workflow-language/common-workflow-language",
      download_url="https://github.com/common-workflow-language/common-workflow-language",
      license='Apache 2.0',
      packages=["cwltool"],
      package_data={'cwltool': ['schemas/draft-1/*', 'schemas/draft-2/*']},
      install_requires=[
          'jsonschema >= 2.4.0',
          'requests',
          'PyYAML',
          'avro',
          'rdflib',
          'rdflib-jsonld'
        ],
      test_suite='tests',
      tests_require=[],
      entry_points={
          'console_scripts': [ "cwltool=cwltool.main:main" ]
      },
      zip_safe=False,
      cmdclass={'egg_info': tagger},
)

