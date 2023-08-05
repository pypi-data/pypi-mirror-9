import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dervisher",
    version = "0.0.5",
    author = "Luke Samaha",
    author_email = "lwsamaha@gmail.com",
    description = ("Demonstrates use of AWS kinesis and dynamodb for application events."),
    license = "BSD",
    keywords = "aws kinesis dynamodb event",
    url = "http://packages.python.org/dervisher",
    packages=['dervisher'],
    entry_points = {'console_scripts':['dervisher = dervisher.whirling:main']}
)

classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7'
]

