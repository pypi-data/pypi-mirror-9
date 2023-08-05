#! /usr/bin/env python

from setuptools import setup

setup(
    name="django-angular-template-i18n-lint",
    version="0.1",
    author="Arabel.la",
    author_email="jacek@arabel.la",
    py_modules=['django_angular_template_i18n_lint'],
    license='GPLv3+',
    url='https://github.com/ArabellaTech/django-angular-template-i18n-lint/',
    description='Lint tool to find non-trans/blocktrans/|translate text in django/angular templates',
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'console_scripts': [
            'django-angular-template-i18n-lint = django_angular_template_i18n_lint:main',
        ]
    },
)
