from setuptools import setup, find_packages

setup(
    name='objectbdd',
    version='0.1.1',
    description="A simple tool for working through a BDD scenario with objects",
    author='Adam Berlin',
    author_email='berlin.ab+objectbdd@gmail.com',
    url='github.com/berlin-ab',
    packages=find_packages(exclude=['tests']),
    install_requires=[
    ],
)
