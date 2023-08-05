# /setup.py
#
# Installation and setup script for polysquare-generic-file-linter
#
# See LICENCE.md for Copyright information
"""Installation and setup script for polysquare-generic-file-linter."""

from setuptools import find_packages
from setuptools import setup

setup(name="polysquare-generic-file-linter",
      version="0.0.13",
      description="Polysquare Style Guide Linter",
      long_description_markdown_filename="README.md",
      author="Sam Spilsbury",
      author_email="smspillaz@gmail.com",
      url="http://github.com/polysquare/polysquare-generic-file-linter",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      license="MIT",
      keywords="development linters",
      packages=find_packages(exclude=["tests"]),
      install_requires=["setuptools"],
      extras_require={
          "test": ["coverage",
                   "nose",
                   "nose-parameterized",
                   "testtools"]
      },
      entry_points={
          "console_scripts": [
              "polysquare-generic-file-linter=polysquarelinter.linter:main"
          ]
      },
      test_suite="nose.collector",
      zip_safe=True,
      include_package_data=True)
