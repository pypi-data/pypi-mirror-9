# Copyright (c) 2015 Codenomicon Ltd.
# License: MIT

from codecs import open
from setuptools import setup, find_packages

from appcheck import __version__ as version

with open('README.rst', encoding='ascii') as f:
    long_description = f.read()

setup(name='appcheck',
      description="Codenomicon Appcheck command line tools and API client",
      url='https://bitbucket.org/codenomicon/appcheck-cli',
      long_description=long_description,
      author='Joonas Kuorilehto',
      author_email='joonas.kuorilehto@codenomicon.com',
      version=version,
      packages=find_packages(exclude=['tests']),
      zip_safe=False,
      install_requires=['click', 'requests', 'keyring'],
      entry_points="""
          [console_scripts]
          appcheck = appcheck.cli:main
      """,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Topic :: Security",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries",
          "Topic :: Utilities",
        ],
      )
