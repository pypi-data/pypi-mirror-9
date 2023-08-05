from distutils.core import setup
from os import path

setup(
    name='resauce',
    author="Makerlabs",
    author_email="hello@makerlabs.co.uk",
    version='0.0.3a4',
    py_modules=['resauce'],
    install_requires=[
        "Flask>=0.10.1",
        "Flask-SQLAlchemy>=2.0",
        "flask-marshmallow>=0.2.0",
        "colander>=1.0b1",
        "dictalchemy>=0.1.2.6",
        "ColanderAlchemy>=0.3.1",
    ]
)
