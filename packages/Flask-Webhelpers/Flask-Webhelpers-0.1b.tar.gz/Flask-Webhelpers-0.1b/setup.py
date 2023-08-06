"""
Flask-Webhelpers
=========

Simple integration of Flask and Webhelpers

Links
-----

* `documentation <https://www.techchorus.net>`_

"""
import re
from setuptools import setup

setup(
    name='Flask-Webhelpers',
    version='0.1b',
    url='https://github.com/bngsudheer/Flask-Webhelpers',
    license='BSD',
    author='Sudheer Satyanarayana',
    author_email='sudheer.zzz@sudheer.net',
    maintainer='Sudheer Satyanarayana',
    maintainer_email='sudheer.zzz@sudheer.net',
    description='Simple integration of Flask and Webhelpers',
    long_description=__doc__,
    packages=['flask_webhelpers'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Webhelpers'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
