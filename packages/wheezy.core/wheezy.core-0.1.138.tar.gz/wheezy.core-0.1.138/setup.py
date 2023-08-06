#!/usr/bin/env python

import os

try:
    from setuptools import setup
except:
    from distutils.core import setup  # noqa

extra = {}
try:
    from Cython.Build import cythonize
    p = os.path.join('src', 'wheezy', 'core')
    extra['ext_modules'] = cythonize(
        [os.path.join(p, '*.py')],
        exclude=os.path.join(p, '__init__.py'),
        nthreads=2, quiet=True)
except ImportError:
    pass

try:
    import uuid  # noqa
except ImportError:
    extra['install_requires'] = ['uuid']

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='wheezy.core',
    version='0.1',
    description='A lightweight core library',
    long_description=README,
    url='https://bitbucket.org/akorn/wheezy.core',

    author='Andriy Kornatskyy',
    author_email='andriy.kornatskyy at live.com',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: System :: Benchmark'
    ],
    keywords='core benchmark collections config datetime db descriptor '
             'feistel i18n introspection json luhn mail pooling url uuid',
    packages=['wheezy', 'wheezy.core'],
    package_dir={'': 'src'},
    namespace_packages=['wheezy'],

    zip_safe=False,
    extras_require={
        'dev': [
            'uuid',
            'wsgiref',
            'coverage',
            'nose',
            'pytest',
            'pytest-pep8',
            'pytest-cov'
        ]
    },

    platforms='any',
    **extra
)
