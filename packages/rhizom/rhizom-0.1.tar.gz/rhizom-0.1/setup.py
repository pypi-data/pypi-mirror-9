#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

def reqfile(filepath):
    """Turns a text file into a list (one element per line)"""
    result = []
    import re
    url_re = re.compile(".+:.+#egg=(.+)")
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            mo = url_re.match(line)
            if mo is not None:
                line = mo.group(1)
            result.append(line)
    return result


setup(
    name="rhizom",
    version="0.1",
    description="Visualize your relationships",
    long_description=open('README.md').read(),
    author='Aurelien Bompard',
    author_email='aurelien@bompard.org',
    url="https://gitlab.com/abompard/rhizom",
    license="AGPLv3+",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 2",
        ],
    packages=find_packages(),
    #include_package_data=True,
    install_requires=reqfile("requirements.txt"),
    #test_suite = "rhizom.test",
    entry_points={
        'console_scripts': [
            'rhizom = rhizom.scripts:main',
            ],
        },
    )
