# coding=utf-8
from setuptools import setup, find_packages

setup(
    name="git-up",
    version="1.3.0",
    packages=find_packages(exclude=["tests"]),
    scripts=['PyGitUp/gitup.py'],
    install_requires=['GitPython==1.0.0', 'colorama==0.3.3',
                      'termcolor==1.1.0', 'docopt==0.6.2',
                      'six==1.9.0'],

    # Tests
    test_suite="nose.collector",
    tests_require='nose',

    # Executable
    entry_points={
        'console_scripts': [
            'git-up = gitup:run'
        ]
    },

    # Additional data
    package_data={
        'PyGitUp': ['check-bundler.rb'],
        '': ['README.rst', 'LICENCE']
    },

    zip_safe=False,

    # Metadata
    author="Markus Siemens",
    author_email="markus@m-siemens.de",
    description="A python implementation of 'git up'",
    license="MIT",
    keywords="git git-up",
    url="https://github.com/msiemens/PyGitUp",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"
    ],

    long_description=open('README.rst').read()
)
