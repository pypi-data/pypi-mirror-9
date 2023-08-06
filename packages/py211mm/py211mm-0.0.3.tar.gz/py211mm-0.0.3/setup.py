import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "py211mm",
    version = "0.0.3",
    author = "Alexander A Kaurov",
    author_email = "akaurov@gmail.com",
    description = ("Tool for generating mock catalogs for 21cm experiments."),
    license = "MIT",
    keywords = "astronomy astrophysics 21cm reionization",
    url = "https://bitbucket.org/kaurov/211mm",
    packages=['py211mm'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        'Programming Language :: Python :: 2.7',
    ],
    install_requires = ['numpy>=1.7', 'cosmolopy'],
    setup_requires = ['numpy>=1.7', 'cosmolopy'],
    scripts = ['scripts/example01.py'],
    include_package_data = True,
    package_data = {
        'py211mm': ['fits/*'],
    },
)
