#!/usr/bin/env python
from setuptools import setup, find_packages


__version__ = "0.0.1"

requirements_file = "requirements.txt"
requirements = [pkg.strip() for pkg in open(requirements_file).readlines()]
test_requirements = ['coverage']

long_description = open('README.rst').read() + "\n"

setup(
    name='mockie',
    version=__version__,
    license='License :: OSI Approved :: MIT License',
    description="Helper classes for easier mocking and patching tests.",
    long_description=long_description,
    author='Marcwebbie',
    author_email='marcwebbie@gmail.com',
    url='https://github.com/marcwebbie/mockie',
    download_url='https://pypi.python.org/pypi/mockie',
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
)
