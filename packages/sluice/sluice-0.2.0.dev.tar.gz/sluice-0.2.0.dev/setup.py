from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sluice',
    version='0.2.0.dev',
    description='Tools for managing zfs snapshots',
    long_description=long_description,

    url='https://bitbucket.org/sjdrake/sluice',
    author='Stephen Drake',
    author_email='steve@synergyconsultingnz.com',

    license='Common Development and Distribution License (CDDL)',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='zfs',

    packages=['sluice'],

    install_requires=[
        'weir==0.2.0.dev',
    ],

    entry_points = {
        'console_scripts': [
            'zfs-autosnapshot = sluice.autosnapshot:main',
            'zfs-copy = sluice.copy:main',
            'zfs-sync = sluice.sync:main',
        ],
    }
)
