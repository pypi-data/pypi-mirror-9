"""Setup.py for restpy."""

from setuptools import find_packages
from setuptools import setup


with open('README.rst') as f:

    README = f.read()

with open('requirements.txt') as f:

    REQUIREMENTS = f.readlines()

setup(
    name='RESTpy',
    version='0.7.0',
    url='https://github.com/kevinconway/rest.py',
    license='BSD',
    description='Werkzeug extensions for building RESTful services.',
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    long_description=README,
    classifiers=[],
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    install_requires=REQUIREMENTS,
)
