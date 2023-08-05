import os
from glob import glob

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    """
    Read a text file and return its contents
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


__version__ = read(
    "src/vernissage/__init__.py"
).split("\n")[0].split("=")[1].strip(" '\"")

setup(
    name="django-vernissage",
    version=__version__,
    license="MIT",
    description=("An extremely simple dynamic TemplateView for django"),
    long_description=read('README.md'),
    author="Tomas Neme",
    author_email="lacrymology@gmail.com",
    url="https://github.com/Lacrymology/django-vernissage",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[os.path.splitext(os.path.basename(path))[0]
                for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    keywords=["django", "image-gallery", "filer django-cms"],
    install_requires=[
        'django-admin-sortable2',
    ],
)
