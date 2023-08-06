import os
from setuptools import setup, find_packages
import multiprocessing

def readme():
  with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    return f.read()

setup(name='path_pipe_conf_tools',
      version='0.0.2',
      description='Tools for working with the pathogen pipeline at The Wellcome Trust Sanger Institute',
      long_description=readme(),
      url='https://github.com/sanger-pathogens/PathPipeConfTools',
      author='Ben Taylor',
      author_email='ben.taylor@sanger.ac.uk',
      scripts=['scripts/list-pathogen-pipeline-jobs'],
      include_package_date=True,
      test_suite='nose.collector',
      tests_require=[
        'nose',
        'mock'
      ],
      license='GPLv3',
      packages=find_packages(),
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
       ]
)
