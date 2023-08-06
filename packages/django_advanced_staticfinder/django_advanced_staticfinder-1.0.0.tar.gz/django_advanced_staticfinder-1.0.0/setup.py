from distutils.core import setup

import advanced_staticfinder

setup(
    name = "django_advanced_staticfinder",
    version = advanced_staticfinder.__version__,
    description = "Menu helpers for django projects",
    url = "https://bitbucket.org/megatyumen/django_advanced_staticfinder",
    author = "Alrusdi",
    author_email = "alrusdi@gmail.com",
    packages = [
        "advanced_staticfinder",
    ],
    package_data = {
        "advanced_staticfinder": [
            "advanced_staticfinder/*",
        ],
    },
    long_description = open("README.rst").read(),
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)

