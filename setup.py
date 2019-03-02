# coding=utf-8
"""
Setup script that pulls information from ~/src/part117_calculator.__init__.py

"""

import codecs
import os
import re
import sys

from setuptools import setup, find_packages


if sys.version_info < (3, 6):
    print('ERROR: AviationWeather requires Python 3.6')
    sys.exit(1)

NAME = "AviationWeather"
PACKAGES = find_packages(where="src")
META_PATH = os.path.join('src', '__init__.py')
KEYWORDS = "aviation weather metar taf airmet sigmet"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: Other/Proprietary License",
    "Operating System :: POSIX",
    "Operating System :: POSIX :: BSD",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.6",
]
INSTALL_REQUIRES = ['zeep', 'lxml', 'python-dateutil', 'PyMySQL', 'requests', 'PyGeodesy', 'SQLAlchemy']

SETUP_REQUIRES = ['pytest-runner']

TESTS_REQUIRE = ['pytest', 'pytest-cov', 'mypy', 'Sphinx', 'sqlalchemy-utils']

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as file:
        return file.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{}__ string.".format(meta))


# Get the long description from the README file
with open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = find_meta("version")
LONG = (
    read("README.rst")
    + "\n\n"
    + '=============='
    + '\n\n'
    + read('CHANGELOG.rst')
)


if __name__ == '__main__':
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=read("README.rst"),
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        setup_requires=SETUP_REQUIRES,
        tests_require=TESTS_REQUIRE,
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'calculations = src.calculations:main',
                'converter = src.converter:main'
            ]
        },
    )
