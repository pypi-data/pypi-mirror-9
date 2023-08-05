#!/usr/bin/env python
# coding=utf-8

import sys
import os

CURRENT_PATH = os.getcwd()
BASE_PATH = CURRENT_PATH
PYTHON_VERSION = sys.version_info.major
input = raw_input if PYTHON_VERSION == 2 else input

joinpath = lambda p, name: os.path.join(p, name)

def cin(prompt='', default_input=''):
    tmp = input(prompt)
    # tmp = tmp.strip()
    return default_input if not tmp else tmp

def delete(p, filename):
    if os.path.exists(joinpath(p, filename)):
        os.remove(joinpath(p, filename))


def make():

    # tips:
    print('##########################################')
    print('#    Welcome to use Makesetup Program    #')
    print('##########################################')

    delete_old = cin('Would you like to delete old setup files ? (y|N)')
    if delete_old.lower() not in ('y', 'Y', 'yes', 'Yes', 'YES'):
        print('\n  You have rejected to delete old setup file.')
        print('So cancel this program.\n')
        sys.exit(-1)

    # 1
    proj_path = cin('\nProject Path: ', CURRENT_PATH)
    proj_name = cin('Project Name: ', None)
    proj_dir = cin('Project Dir: ', None)
    version = cin('Version: ', '0.0.1')
    description = cin('Description: ')
    author = cin('Author: ')
    author_email = cin('Author Email: ')
    requires = cin('Requires (separate with ","): ').split(',')

    home_page = cin('Home Page: ')
    license = cin('License: ', 'Apache 2.0')
    is_console_scripts = cin('Is Console Scripts ?(If yes, make sure proj_dir.__init__.py has a function named `main`) (y|N): ', 'n')
    # summary = cin('Summary: ')
    # keywords = cin('Keywords: ')
    # platform = cin('Platform: ', 'Linux/Unix')
    # download_url = cin('Download URL: ')
    # provider = cin('Provider: ')
    # classifiers = input('Classifiers: ')
    classifiers = (
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        )
    # zip_safe = False

    ## delete old files
    delete(proj_path, 'setup.py')
    delete(proj_path, 'README.rst')
    delete(proj_path, 'HISTORY.rst')
    delete(proj_path, 'README.md')
    ##

    with open(joinpath(proj_path, 'README.rst'), 'w') as fp:
        fp.write('Project: %s \n-----------------------\n' % proj_name)

    with open(joinpath(proj_path, 'HISTORY.rst'), 'w') as fp:
        fp.write('Project History: %s \n-----------------------\n' % proj_name)

    with open(joinpath(proj_path, 'setup.py'), 'w') as fp:
        # base
        fp.write('''
#!/usr/bin/env python 
# coding=utf-8
        
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    with open('README.rst', 'r') as fp:
        readme = fp.read()
except :
    readme = ''
try:
    with open('README.md', 'r') as fp:
        readme = fp.read()
except :
    pass

try:
    with open('HISTORY.rst', 'r') as fp:
        history = fp.read()
except :
    history = ''
        ''')

        fp.write('\n\nsetup(\n')
        # Package Info Begin

        fp.write('    name = \'%s\',\n' % proj_name)
        fp.write('    version = \'%s\',\n' % version)
        fp.write('    description = \'%s\',\n' % description)
        fp.write('    long_description = readme + history,\n')
        fp.write('    author = \'%s\',\n' % author)
        fp.write('    author_eamil = \'%s\',\n' % author_email)
        fp.write('    url = \'%s\',\n' % home_page)
        fp.write('    packages = %s,\n' % proj_name.split(','))
        fp.write('    package_dir = {"%s": "%s"},\n' % (proj_name, proj_dir))
        fp.write('    include_package_data = True,\n')
        fp.write('    install_requires = %s,\n' % requires)
        fp.write('    license = "%s",\n' % license)
        fp.write('    zip_safe = False,\n')
        fp.write('    classifiers = %s,\n' % str(classifiers))
        if is_console_scripts.lower() in ['y', 'yes']:
            fp.write('    entry_points = {"console_scripts": ["%s = %s:main"]},\n' % (proj_name, proj_name))

        # Package Info End
        fp.write('\n)\n')

if __name__ == '__main__':
    make()
