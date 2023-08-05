from setuptools import setup


def readfile(fname):
    with open(fname) as f:
        return f.read()


setup(
    name="Ermes",
    version="0.1a",
    license="ISC",
    author="Cosmia Fu",
    author_email="cosmiafu@gmail.com",
    description="Socks5 proxy client for Python",
    long_description=readfile("README.rst"),
    py_modules=["ermes"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
