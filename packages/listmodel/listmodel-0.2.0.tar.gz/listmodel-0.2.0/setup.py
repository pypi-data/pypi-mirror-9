import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    long_description = readme.read()

setup(
    name="listmodel",
    version="0.2.0",
    description="Listmodel is a Python library for object mappings for "
                "various list sources (XML documents, CSV documents, text "
                "documents, JSON/YAML objects) in a unified manner.",
    long_description=long_description,
    license="LGPL v3",
    url="http://github.com/jackuess/listmodel",

    author="Jacques de Laval",
    author_email="jacques@tuttosport.se",

    packages=["listmodel"],

    install_requires=[
        "jsonpath_rw",
        "lxml",
        "pyyaml"
    ],
    tests_require=["nose"],
    test_suite="nose.collector",
    extras_require={
        "docs": ["sphinx"]
    }
)
