import os
from uuid import uuid4
from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=uuid4())
reqs = [str(ir.req) for ir in install_reqs]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "dervisher",
    version = "0.0.7",
    author = "Luke Samaha",
    author_email = "lwsamaha@gmail.com",
    description = ("Demonstrates use of AWS kinesis and dynamodb for application events."),
    license = "BSD",
    keywords = "aws kinesis dynamodb event",
    url = "http://packages.python.org/dervisher",
    packages = ['dervisher'],
    install_requires = reqs,
    entry_points = {'console_scripts':['dervisher = dervisher.whirling:main']}
)

classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7'
]

