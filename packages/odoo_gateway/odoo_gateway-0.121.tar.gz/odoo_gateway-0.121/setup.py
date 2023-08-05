# encoding=utf-8

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="odoo_gateway",
    version="0.121",
    author="Panaetov Alexey",
    author_email="panaetovaa@gmail.com",
    description=(
        "Shell and reference to models in stand-alone applications for Odoo"
    ),
    long_description=read('README.rst'),
    license = "BSD",
    keywords = "odoo openerp shell models stand-alone",
    url = "https://bitbucket.org/panaetov/odoo_gateway/overview",
    packages=['odoo_gateway'],
    classifiers=[],
    entry_points="""
    # ...
    [console_scripts]
    odoosh = odoo_gateway:shell
    """,
)
