# -*- coding: utf-8 -*-
import sys
from distutils.core import setup

setup(
    name='clg',
    version='1.1',
    author='François Ménabé',
    author_email='francois.menabe@gmail.com',
    url='https://clg.readthedocs.org/en/latest/',
    download_url='https://github.com/fmenabe/python-clg',
    license='MIT License',
    description='Command-line generator from a dictionary.',
    long_description=open('README.rst').read(),
    keywords=['command-line', 'argparse', 'wrapper', 'YAML', 'JSON'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    py_modules=['clg'],
    install_requires=['six']
)
