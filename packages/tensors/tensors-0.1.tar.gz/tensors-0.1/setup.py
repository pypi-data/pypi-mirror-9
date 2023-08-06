import setuptools


configuration = {
    "name": "tensors",
    "version": "0.1",
    "description": "Interface for working with low-rank tensor approximations",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    "keywords": "tensor low-rank TT vector matrix",
    "url": "https://bitbucket.org/thoughteer/tensors",
    "author": "Iskander Sitdikov",
    "author_email": "thoughteer@gmail.com",
    "license": "MIT",
    "packages": setuptools.find_packages(exclude=["tests"]),
    "install_requires": ["beswitch>=0.1", "tt>=0.1"],
    "zip_safe": False
}
setuptools.setup(**configuration)
