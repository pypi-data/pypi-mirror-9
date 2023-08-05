try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import malibu

setup(
    name = 'malibu',
    version = malibu.__version__,
    description = "maiome's library of utilities",

    url = "http://phabricator.maio.me/tag/malibu",
    author = "Sean Johnson",
    author_email = "sean.johnson@maio.me",
    
    license = "Unlicense",
    
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages = ['malibu',
                'malibu.config',
                'malibu.connection',
                'malibu.database',
                'malibu.text',
                'malibu.util'],
    package_dir = {'malibu': 'malibu'},
    zip_safe = True
)
