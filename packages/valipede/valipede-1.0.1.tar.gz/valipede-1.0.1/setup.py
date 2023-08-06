import io
import os.path
from setuptools import setup, find_packages

setup(
	name='valipede',
	version="1.0.1",
	description='Data validation',
	long_description=io.open('README.rst', mode='r', encoding='utf-8').read(),
	classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='validation',
    author='Elisha Fitch-Cook',
    author_email='elisha@cooper.com',
    url='http://github.com/cooper-software/valipede',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'six',
        'simpleobserver'
    ],
    tests_require=[
        'mock',
        'timelib', 
        'python-dateutil'
    ],
    test_suite='test_valipede'
)