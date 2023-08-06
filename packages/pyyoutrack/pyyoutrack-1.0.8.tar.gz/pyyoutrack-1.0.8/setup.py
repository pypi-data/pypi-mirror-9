__author__ = 'kkrzysztofik'

from setuptools import setup
from version import version

setup(
    name='pyyoutrack',
    version=version,
    packages=['youtrack'],
    maintainer='Krzysztof Krzysztofik',
    maintainer_email='kkrzysztofik@teonite.com',
    url='https://github.com/teonite/youtrack-rest-python-library',
    description='Python library that wraps YouTrack REST API.',
    license='Apache License, Version 2.0',
    install_requires=[
        "httplib2 >= 0.7.4",
        "urllib2_file",
        "poster",
        "six"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7"
    ]
)
