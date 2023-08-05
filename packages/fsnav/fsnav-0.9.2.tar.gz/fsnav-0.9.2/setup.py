#!/usr/bin/env python


"""
Setup script for FS Nav
"""


import os
import setuptools


with open('README.md') as f:
    readme = f.read().strip()


with open('LICENSE.txt') as f:
    license = f.read().strip()


with open('requirements.txt') as f:
    install_requires = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('fsnav', 'settings.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break

setuptools.setup(
    name='fsnav',
    version=version,
    author=author,
    author_email=email,
    description="FS Nav - File System Navigation shortcuts for the commandline",
    long_description=readme,
    url=source,
    license=license,
    packages=setuptools.find_packages(),
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    include_package_data=True,
    zip_safe=True,
    keywords='commandline shortcut alias navigation',
    install_requires=install_requires,
    entry_points="""
        [console_scripts]
        count=fsnav.cmdl.count:main
        nav=fsnav.cmdl.nav:main
    """
)
