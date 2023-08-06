from setuptools import setup

with open('readme.rst') as file:
	README = file.read()


setup(name='tinyble',
	  version='0.1.4.4',
	  description='A tiny NoSQL database with in-memory caching',
	  long_description=README,
	  url='https://github.com/StevenSLXie/tinyble',
	  author='Steven S.L. Xie',
	  author_email='stevenslxie@gmail.com',
	  license='MIT',
	  packages=['tinyble'],
	  zip_safe=False)