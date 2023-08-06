from setuptools import setup

file = open('readme.rst')
try:
	README = file.read()
finally:
	file.close()

setup(name='tinyble',
	  version='0.1.4.5',
	  description='A tiny NoSQL database with in-memory caching',
	  long_description=README,
	  url='https://github.com/StevenSLXie/tinyble',
	  author='Steven S.L. Xie',
	  author_email='stevenslxie@gmail.com',
	  license='MIT',
	  packages=['tinyble'],
	  zip_safe=False)