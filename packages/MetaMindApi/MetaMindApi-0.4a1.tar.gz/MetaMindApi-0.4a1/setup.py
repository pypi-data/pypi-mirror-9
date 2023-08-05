from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

setup(
    name='MetaMindApi',
    version="0.4a1",
    description="MetaMind client for text and image classification",
    long_description="", #TODO: write
    url="https://www.metamind.io", # TODO: use existing API page, or create new API page
    author="MetaMind Team",
    author_email="contact@metamind.io",
    license="", #TODO,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
        #"License :: ??", #TODO
    ],
    keywords="metamind api",
    packages=['metamind','metamind.api'],
    install_requires=["requests","simplejson"]
)
