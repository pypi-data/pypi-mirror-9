#!/usr/bin/env python

from distutils.core import setup
from uwsgi_cache import __VERSION__

setup(name='uwsgi_cache',
        version=__VERSION__,
        description='Python uWSGI caching wrappers',
        author="Kellen Fox",
        author_email="kellen@cablespeed.com",
        url="https://github.com/Kellel/uwsgi-cache/",
        packages=["uwsgi_cache"],
        )
