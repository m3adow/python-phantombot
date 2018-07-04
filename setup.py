import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phantombot",
    version="0.0.1",
    author="Till Wiese",
    author_email="mail-pypi.org@till-wiese.de",
    description="Python module to communicate with the PhantomBot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m3adow/python-phantombot/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
