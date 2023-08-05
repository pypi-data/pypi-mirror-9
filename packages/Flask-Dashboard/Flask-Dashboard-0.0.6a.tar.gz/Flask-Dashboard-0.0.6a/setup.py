from setuptools import setup, find_packages


def readfile(fname):
    with open(fname) as f:
        return f.read()


setup(
    name="Flask-Dashboard",
    version="0.0.6a",
    license="BSD",
    author="Cosmia Fu",
    author_email="cosmiafu@gmail.com",
    description="Yet another admin interface for Flask",
    long_description=readfile("README.rst"),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=readfile("requirements.txt"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
