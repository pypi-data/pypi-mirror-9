import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    

setup(
    name = "mathgraph",
    version = "0.0.2",
    description = "",
    long_description = read('README.md'),
    url = 'https://pypi.python.org/pypi/mathgraph',
    license = 'MIT',
    author = 'Sudharsan Vijayaraghavan',
    author_email = 'sudvijayr@gmail.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    install_requires = ['numpy', 'networkx', 'mathchem']

)
