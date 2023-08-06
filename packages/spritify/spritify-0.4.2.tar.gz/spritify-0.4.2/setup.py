# -*- coding: utf-8 -*-
'''
Copyright 2012 Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from setuptools import setup

__version__ = '0.4.2'


def get_long_description():
    try:
        text = open('README.rst', 'r').read()
    except:
        text = None
    finally:
        return text

setup(
    name='spritify',
    description='The spritify is a tool for transform directory of images in the stylesheet and image file.',
    long_description=get_long_description(),
    version=__version__,
    home='https://bitbucket.org/rodrigopmatias/spritify',
    author='Rodrigo Pinheiro Matias',
    author_email='rodrigopmatias@gmail.com',
    maintainer='Rodrigo Pinheiro Matias',
    maintainer_email='rodrigopmatias@gmail.com',
    py_modules=['res'],
    scripts=['spritify.py'],
    install_requires=['pillow', 'jinja2'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics :: Editors',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
