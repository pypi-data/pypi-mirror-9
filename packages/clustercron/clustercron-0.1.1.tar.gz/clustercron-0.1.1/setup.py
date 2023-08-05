#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    'pytest',
]

setup(
    name='clustercron',
    version='0.1.1',
    description='Cron job wrapper that ensures a script gets run from one node in the cluster.',
    long_description=readme + '\n\n' + history,
    author='Maarten Diemel',
    author_email='maarten@maartendiemel.nl',
    url='https://github.com/maartenq/clustercron',
    packages=[
        'clustercron',
    ],
    package_dir={'clustercron':
                 'clustercron'},
    entry_points={
        'console_scripts': [
            'clustercron = clustercron.clustercron:main',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='clustercron',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
