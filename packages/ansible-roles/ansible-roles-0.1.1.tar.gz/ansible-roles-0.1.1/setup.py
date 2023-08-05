import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

from ansible_roles import __version__

setup(
    name='ansible-roles',
    version=__version__,
    description='Manage ansible roles.',
    long_description=(read('README.md')),
    url='https://pikacode.com/meister/ansible-roles',
    keywords='ansible roles',
    license='MIT',
    author='Benjamin Jorand',
    author_email='benjamin.jorand@gmail.com',
    scripts=['bin/ansible-roles'],
    packages=["ansible_roles"],
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License'
    ],
)
