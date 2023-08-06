import os
from setuptools import setup, find_packages
import multiprocessing

def readme():
  with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    return f.read()

setup(name='jsontoemail',
      version='0.0.5',
      description='Deprecated: please use json2email instead',
      url='https://github.com/sanger-pathogens/json2email',
      author='Ben Taylor',
      author_email='ben.taylor@sanger.ac.uk',
      scripts=['scripts/json-to-email'],
      include_package_data=True,
      install_requires=[],
      tests_require=[],
      license='GPLv3',
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Email",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities"
      ]
)
