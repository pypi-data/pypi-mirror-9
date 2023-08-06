#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


def main ():
    setup (
        name = 'python-rco',
        version = '0.2.2',
        description = 'RC Online services library',
        long_description = 'RC Online services library',
        author = 'Ruslan V. Uss',
        author_email = 'unclerus@gmail.com',
        # url = 'https://github.com/UncleRus/cherryBase',
        license = 'LGPLv3',
        packages = ('rco',),
        install_requires = ['cherrybase >= 0.3.8', 'pgpxmlrpc >= 1.1.1', 'regnupg >= 0.3.5']
    )


if __name__ == "__main__":
    main ()
