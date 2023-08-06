__author__ = 'Henning Gross'
from ez_setup import use_setuptools
use_setuptools()
import sys
import platform
from setuptools import setup, find_packages

p = platform.platform().lower()
if "darwin" in p:
    try:
        import py2app
    except ImportError:
        pass
elif "win" in p:
    try:
        import py2exe
    except ImportError:
        pass

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    #extra['convert_2to3_doctests'] = ['src/your/module/README.txt']
    #extra['use_2to3_fixers'] = ['your.fixers']

# http://www.py2exe.org/index.cgi/ListOfOptions
setup(
    #app=["MyApplication.py"],
    #setup_requires=["py2app"],
    install_requires = [
        "requests>=2.4.3",
        "beautifulsoup4>=4.3.2",
        "chardet>=2.3.0",
        "html5lib>=0.999",
        "simple-crypt>=3.0.2",
        "CherryPy>=3.6.0",
        "psutil>=2.1.3"
    ],
    name='speedwise-node',
    url='http://speedwise.de',
    version = '0.1.13.1',
    description='This is the server node module to connect your Assetto Corsa game servers with speedwise.de.',
    long_description=open('README.rst').read(),
    author='Henning Gross',
    author_email='mail.to <at> henning-gross <dot> de',
    license='MIT',
    packages = find_packages(),
    package_data = {
        '': ['*.txt', '*.rst', '*.ini'],
    },
    entry_points={
        'console_scripts': [
            'speedwise-ac-server-wrapper = hgross.ac.ACServerWrapper:main_func',
            'speedwise-ac-log-parser = hgross.ac.ACLogParser:main_func',
            'speedwise-node = hgross.speedwise_node:main_func'
        ],
        #'gui_scripts': [
        #    'baz = my_package_gui:start_func',
        #]
    },
    console=[
            'hgross/ac/ACServerWrapper.py',
            'hgross/ac/ACLogParser.py',
            'hgross/speedwise_node.py'
        ],
    keywords=[
            'assetto corsa', 'ac', 'speedwise', 'stats', 'statistics', 'monitoring', 'banlist', 'server', 'dedicated server', 'gameserver', 'game', 'racing'
        ],
    classifiers= [
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: Microsoft',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
    ],
    **extra
)