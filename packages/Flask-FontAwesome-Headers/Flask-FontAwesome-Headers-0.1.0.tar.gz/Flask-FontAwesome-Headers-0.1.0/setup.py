import os

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 'flask_fontawesome_headers.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="Flask-FontAwesome-Headers",
    version=__version__,
    url="https://github.com/Jaza/flask-fontawesome-headers",

    author="Jeremy Epstein",
    author_email="jazepstein@gmail.com",

    description="Sets CORS HTTP response headers for Font-Awesome files served by Flask's send_file().",
    long_description=open('README.rst').read(),

    py_modules=['flask_fontawesome_headers'],
    zip_safe=False,
    platforms='any',

    install_requires=['Flask'],

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
