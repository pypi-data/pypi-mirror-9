#!/usr/bin/env python

import os
from pip.download import PipSession
from pip.index import PackageFinder
from pip.req import parse_requirements
from setuptools import setup, find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(root_dir, 'requirements', 'base.txt')

session = PipSession()
finder = PackageFinder([], [], session=session)
requirements = parse_requirements(requirements_path, finder, session=session)
install_requires = [str(r.req) for r in requirements]

version = '1.5.5'  # Update docs/CHANGELOG.rst if you increment the version

setup(
    name="django-nose-qunit",
    version=version,
    author="Jeremy Bowman",
    author_email="jbowman@safaribooksonline.com",
    description="Integrate QUnit JavaScript tests into a Django test suite via nose",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    url='https://github.com/safarijv/django-qunit-ci',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={
        'django_nose_qunit': [
            'static/*.css',
            'static/*.js',
            'static/django_nose_qunit/test/*.js',
            'templates/django_nose_qunit/*.html',
            'templates/django_nose_qunit/fixtures/*.html',
        ],
    },
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'nose.plugins.0.10': [
            'django-qunit = django_nose_qunit.nose_plugin:QUnitPlugin',
            'django-qunit-index = django_nose_qunit.nose_plugin:QUnitIndexPlugin'
        ]
    },
)
