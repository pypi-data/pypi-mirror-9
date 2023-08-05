try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
	name='reactor',
    version='0.1',
    description='Reactor.am python client',
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