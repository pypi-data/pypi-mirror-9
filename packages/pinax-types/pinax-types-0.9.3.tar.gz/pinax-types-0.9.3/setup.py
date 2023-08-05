import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="",
    author_email="",
    description="",
    name="pinax-types",
    long_description=read("README.rst"),
    version="0.9.3",
    url="http://pinax-types.rtfd.org/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.types": []
    },
    test_suite="runtests.runtests",
    tests_require=[
        "python-dateutil>=2.4.0"
    ],
    install_required=[
        "python-dateutil>=2.4.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
