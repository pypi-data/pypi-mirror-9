from setuptools import setup

setup(
name='LDAP-Hopper',
version='3.0.1',
author='Brian Wiborg',
author_email='baccenfutter@c-base.org',
packages=['ldap_hopper'],
scripts=[],
url='http://pypi.python.org/pypi/LDAP-Hopper/',
license='LICENSE.txt',
description='Simple access to LDAP Directory Information Tree.',
long_description=open('README.txt').read(),
install_requires=['python-ldap >= 2.4.13'],
)

