from jiver import __version__

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dependencies = ['docopt', 'termcolor']


def publish():
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(
    name='jiver',
    version=".".join(str(x) for x in __version__),
    description='Collection of utilities for a Jive PS engineer',
    long_description=open('README.rst').read(),
    url='http://www.github.com/digitaldarwin/jiver',
    license="MIT License",
    author='Michael Masters',
    author_email='mmasters+jiver@gmail.com',
    install_requires=dependencies,
    packages=['jiver', ],
    entry_points={
        'console_scripts': [
            'jiver=jiver.main:start'
        ],
    },
    data_files=[
        # use homebrew's completion directory
        ('/usr/local/etc/bash_completion.d', ['extra/jiver-completion.sh']),
        ('/usr/local/jiver', ['extra/upgrade-analyzer.jar']),
        ('/usr/local/jiver', ['extra/git-checkout.txt']),
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)

