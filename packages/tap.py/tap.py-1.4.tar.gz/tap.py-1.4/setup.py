# Copyright (c) 2015, Matt Layman
"""
tappy is a set of tools for working with the `Test Anything Protocol (TAP)
<http://testanything.org/>`_, a line based test protocol for recording test
data in a standard way.

Follow tappy development on `GitHub <https://github.com/mblayman/tappy>`_.
Developer documentation is on
`Read the Docs <https://tappy.readthedocs.org/>`_.
"""

from setuptools import find_packages, setup
import sys

__version__ = '1.4'


def install_requirements():
    requirements = [
        'nose',
        'Pygments==2.0.1',
        ]
    if (2, 7, 0) > sys.version_info:
        requirements.append('argparse')

    if (3, 3, 0) > sys.version_info:
        requirements.append('mock')

    return requirements

# The docs import setup.py for the version so only call setup when not behaving
# as a module.
if __name__ == '__main__':
    with open('docs/releases.rst', 'r') as f:
        releases = f.read()

    long_description = __doc__ + '\n\n' + releases

    install_requires = install_requirements()
    # Add some developer tools.
    if 'develop' in sys.argv:
        install_requires.extend([
            'coverage',
            'flake8',
            'Sphinx',
            'tox',
        ])

    setup(
        name='tap.py',
        version=__version__,
        url='https://github.com/mblayman/tappy',
        license='BSD',
        author='Matt Layman',
        author_email='matthewlayman@gmail.com',
        description='Test Anything Protocol (TAP) tools',
        long_description=long_description,
        packages=find_packages(),
        entry_points={
            'console_scripts': ['tappy = tap.main:main'],
            'nose.plugins.0.10': ['tap = tap.plugin:TAP'],
            'pygments.lexers': ['tap = tap.lexer:TAPLexer'],
        },
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=install_requires,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Testing',
        ],
        keywords=[
            'TAP',
            'unittest',
        ],
        test_suite='tap.tests'
    )
