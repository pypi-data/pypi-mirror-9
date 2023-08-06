# -*- coding: utf-8 -*-
"""Setup for ps.releaser package."""

from setuptools import find_packages
from setuptools import setup

version = '0.2'
description = 'Plugins for release automation with zest.releaser.'
long_description = ('\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
]))

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'zest.releaser',
]

setup(
    name='ps.releaser',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    keywords='',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/ps.releaser',
    download_url='http://pypi.python.org/pypi/ps.releaser',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['ps'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'mock',
            'nose',
            'nose-selecttests',
            'unittest2',
        ]
    },
    entry_points={
        'zest.releaser.releaser.after': [
            'release_diazo=ps.releaser.diazo:release_diazo',
        ],
    },
)
