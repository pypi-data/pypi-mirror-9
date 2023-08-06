"""
Setup for indico apis
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="IndicoIo",
    version='0.5.0',
    packages=[
        "indicoio",
        "indicoio.text",
        "indicoio.images",
        "indicoio.utils",
        "tests",
    ],
    description="""
        A Python Wrapper for indico.
        Use pre-built state of the art machine learning algorithms with a single line of code.
    """,
    license="MIT License (See LICENSE)",
    long_description=open("README.rst").read(),
    url="https://github.com/IndicoDataSolutions/indicoio-python",
    author="Alec Radford, Slater Victoroff, Aidan McLaughlin",
    author_email="""
        Alec Radford <alec@indicodatasolutions.com>,
        Slater Victoroff <slater@indicodatasolutions.com>,
        Aidan McLaughlin <aidan@indicodatasolutions.com>
    """,
    setup_requires=[
        "numpy >= 1.8.1",
        "six >= 1.3.0",
    ],
    install_requires=[
        "requests >= 1.2.3",
        "six >= 1.3.0",
        "numpy >= 1.8.1",
        "scikit-image >= 0.10.1",
    ],
)
