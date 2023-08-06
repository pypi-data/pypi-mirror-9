import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__),'README.rst')) as readme:
	README = readme.read()

#allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='pi-annotations',
	version='0.1.0',
	packages=['annotations'],
	include_package_data=True,
	license='GPL v2',
	description='An app to create per-paragraph comments on content (created via Blogging App)',
	author=['Anshul Thakur'],
	author_email=['captain@piratelearner.com'],
	long_description=README,
	url='https://github.com/PirateLearner/annotations',
	download_url='https://github.com/PirateLearner/annotations/archive/v0.1.0.tar.gz',
	install_requires=[
			 "Django ==1.6.8",
			 'pi-blogging==0.1.0b1',
			 'djangorestframework==3.1.0'],
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)


