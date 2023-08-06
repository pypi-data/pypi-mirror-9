from distutils.core import setup

setup(
    # Application name:
    name="Y-Rip",

    # Version number (initial):
    version="2.0.0",

    # Application author details:
    author="Vignesh Waran",
    author_email="validinternet@gmail.com",

    # Packages
    packages=["Yrip"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/Y-Rip/",

    #
    # license="LICENSE.txt",
    description="An(other) Powerful Hashing algorithm.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "hashlib",
    ],
)