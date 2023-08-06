from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires=[
    'weir==0.3.0',
]

# extra requirements for Python 2.6
try:
    import argparse
except ImportError:
    install_requires.append('argparse>=1.3.0')

setup(
    name='sluice',
    version='0.3.0',
    description='Tools for managing zfs snapshots',
    long_description=long_description,

    url='https://bitbucket.org/sjdrake/sluice',
    author='Stephen Drake',
    author_email='steve@synergyconsultingnz.com',

    license='Common Development and Distribution License (CDDL)',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='zfs',

    packages=['sluice'],

    install_requires=install_requires,

    entry_points = {
        'console_scripts': [
            'zfs-autosnapshot = sluice.autosnapshot:main',
            'zfs-copy = sluice.copy:main',
            'zfs-cull = sluice.cull:main',
            'zfs-sync = sluice.sync:main',
        ],
    }
)
