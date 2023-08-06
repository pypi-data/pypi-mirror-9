from setuptools import setup

setup(
	name='wotwrapper',
	version='0.0.4',
	description='A library to wrap a python object onto the Wotio Operating Enviroment',
	url='http://github.com/wotio/wotwrapper',
	author='Andrew Khoury',
	author_email='drew@wot.io',
	license='MIT',
	install_requires=[
		'websocket-client',
		'requests'
	],
	packages=['wotwrapper'],
	zip_safe=False
)
