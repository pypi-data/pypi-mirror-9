try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# load long description
with open('LONG_DESCRIPTION.rst') as f:
    long_description = f.read()


setup(
	name='reactor',
    version='0.1.1',
    description='Reactor.am python client',
    long_description=long_description,
    install_requires=[
		'unittest2',
		'mock',
		'requests',
	],
	url='https://reactor.am/',
	author='Reactor',
	author_email='hello@reactor.am',
    packages=['reactor'],
    classifiers=[
    	'Development Status :: 5 - Production/Stable',
    	'Intended Audience :: Customer Service',
    	'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    	'Programming Language :: Python :: 2.7',
    ]
)