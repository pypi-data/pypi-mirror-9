import os

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 'flask_wtf_alchemy_utils.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="flask-wtf-alchemy-utils",
    version=__version__,
    url="https://github.com/Jaza/flask-wtf-alchemy-utils",

    author="Jeremy Epstein",
    author_email="jazepstein@gmail.com",

    description="Form and field utility base classes for use with Flask, Flask-WTF, and wtforms-alchemy.",
    long_description=open('README.rst').read(),

    py_modules=['flask_wtf_alchemy_utils'],
    zip_safe=False,
    platforms='any',

    install_requires=['Flask', 'Flask-WTF', 'WTForms-Alchemy'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
