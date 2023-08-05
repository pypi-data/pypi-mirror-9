from __future__ import print_function
from setuptools import setup, find_packages
from awsmeta import VERSION
import os
import sys

with open('README.md') as f:
    long_description = f.read()


def per_user_data_files():
    target_dir = os.path.join('etc', 'bash_completion.d')
    if os.geteuid() == 0:
        target_dir = os.path.join('/', target_dir)
    else:
        print('''
        Non-root installation. If you want bash completion, you'll need to
        install it manually. The file is located at <install_dir>/{}/awsmeta
        '''.format(target_dir), file=sys.stderr)
    return [
        (target_dir, ['extras/bash_completion/awsmeta']),
    ]

setup(
    name="awsmeta",
    version=VERSION,
    description="A tool for querying the AWS metadata service from the CLI",
    long_description=long_description,
    author="Matthew Wedgwood",
    author_email="mw@rmn.com",
    url="https://github.com/slank/awsmeta",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
    ],
    license="MIT",
    entry_points={
        "console_scripts": [
            'awsmeta = awsmeta.cli:main',
        ]
    },
    data_files=[
        ('etc/bash_completion.d', ('extras/bash_completion/awsmeta',)),
    ],
)
