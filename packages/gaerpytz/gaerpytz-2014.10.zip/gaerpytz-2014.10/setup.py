"""gaerpytz is like gaepytz but automated so zoneinfo is up-to-date."""

from setuptools import setup
import os.path

import pytz

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from README.rst
with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='gaerpytz',

    # Match the pytz version
    version=pytz.__version__,

    description='gaerpytz is like gaepytz (a version of pytz that works well \
on Google App Engine) but automated so zoneinfo is up-to-date.',
    long_description=long_description,

    # The project's main homepage.
    url='http://gaerpytz.appspot.com/',

    # Author details
    author='gaerpytz',
    author_email='support@gaerpytz.appspotmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',
        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # What does your project relate to?
    keywords='timezone tzinfo datetime olson time',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['pytz'],

    platforms='any',

    # gaerpytz cannot be run as a zipfile because it uses __file__ manipulation
    zip_safe=False,

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'pytz': ['zoneinfo.zip'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={},
)
