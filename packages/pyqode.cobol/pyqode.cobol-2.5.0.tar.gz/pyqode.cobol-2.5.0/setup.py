#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This setup script packages pyqode.python
"""
from setuptools import setup, find_packages
from pyqode.cobol import __version__

#
# add ``build_ui command`` (optional, for development only)
# this command requires the following packages:
#   - pyqt_distutils
#   - pyqode-uic
#
try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    cmdclass = {}


def readme():
    return str(open('README.rst').read())


# get requirements
requirements = [
    'pyqode.core>=2.3'
]


setup(
    name='pyqode.cobol',
    namespace_packages=['pyqode'],
    version=__version__,
    packages=[p for p in find_packages() if 'test' not in p],
    keywords=["CodeEdit PySide PyQt code editor widget cobol"],
    package_dir={'pyqode': 'pyqode'},
    url='https://github.com/pyQode/pyqode.python',
    license='MIT',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='Add COBOL support to pyQode',
    long_description=readme(),
    install_requires=requirements,
    zip_safe=False,
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'
    ]
)
