# from distutils.core import setup
from setuptools import setup

setup(
    name='cisco_pass',
    packages=['cisco_pass'],
    version='0.2',
    description='Generate Cisco password strings.  Decrypt type7.  Devices: IOS, NXOS, ACE, CatOS',
    author='Roger Caldwell',
    author_email='roger@monkey.net',
    url='https://github.com/rcaldwel/cisco_pass',
    download_url='https://github.com/rcaldwel/cisco_pass/tarball/0.2',
    keywords=['cisco', 'password', 'crypt'],
    install_requires=['passlib'],
    classifiers=[],
)