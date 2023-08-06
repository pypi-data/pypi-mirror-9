#!/usr/bin/env python
import os
import setuptools

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setuptools.setup(
        name='fzsl',
        version='0.3',
        description='Fuzzy path searching for shells',
        license='BSD',
        long_description=(read('README.rst')),
        author='Justin Bronder',
        author_email='jsbronder@gmail.com',
        url='http://github.com/jsbronder/fzsl',
        keywords='fuzzy shell search console match ncurses',
        packages=['fzsl'],
        package_data = {
          '': ['*.rst', 'etc/fzsl.*', 'LICENSE'],
        },
        data_files = [
          ('share/fzsl/', ['README.rst', 'LICENSE', 'etc/fzsl.bash', 'etc/fzsl.conf']),
        ],
        scripts=['bin/fzsl'],
        install_requires=['six'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Console :: Curses',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: System :: Shells',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: System Shells',
            'Topic :: Terminals',
            'Topic :: Terminals :: Serial',
            'Topic :: Terminals :: Telnet',
            'Topic :: Terminals :: Terminal Emulators/X Terminals',
            'Topic :: Text Processing :: Filters',
            'Topic :: Utilities',
        ]
)
