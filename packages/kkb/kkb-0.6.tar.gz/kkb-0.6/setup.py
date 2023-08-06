# -*- coding: utf-8 -*-
import os
from setuptools import setup,find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
	README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

CLASSIFIERS = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
    	'Topic :: Software Development :: Build Tools',
		'License :: Freely Distributable',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Topic :: Software Development :: Libraries :: Python Modules',
		]

setup(
	name='kkb',
	version='0.6',
	packages=find_packages(),
	include_package_data=True,
	license='Freely Distributable', 
	description='Django package для работы с КазКоммерцБанк ePay',
	long_description=README,
	url='http://www.decemberapp.com/kkb',
	author='tukhfatov,sofaku',
	author_email='info@decemberapp.com',
	classifiers=CLASSIFIERS,
)