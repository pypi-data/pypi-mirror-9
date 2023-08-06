#!/usr/bin/env python

import drove as project

from setuptools import setup
from setuptools import find_packages


def get_file_content(fname):
    try:
        return open(fname).read()
    except:
        return None


setup(
    name=project.NAME,
    version=project.VERSION,
    description=project.DESCRIPTION,
    long_description=get_file_content('README.rst'),
    author=project.AUTHOR_NAME,
    author_email=project.AUTHOR_EMAIL,
    url=project.URL,
    packages=find_packages(),
    install_requires=["six>=1.8.0", "wcfg>=3"],
    license=project.LICENSE,
    entry_points={
        'console_scripts': [
            '%s = %s.script:main' % (project.NAME, project.NAME,),
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],

    include_package_data=True,
    test_suite="drove.tests",
)
