from distutils.core import setup

import menus

setup(
    name = "django-menus-py3",
    version = menus.__version__,
    description = "Menu helpers for django projects",
    url = "https://github.com/alrusdi/django-admin-bootstrap-legacy",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    maintainer = 'alrusdi',
    maintainer_email = 'alrusdi@gmail.com',
    packages = [
        "menus",
        "menus.templatetags"
    ],
    package_data = {
        "menus": [
            "static/menus/*/*",
            "templates/menu/*",
            "VERSION",
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
