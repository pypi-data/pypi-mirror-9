import io
import os.path
from setuptools import setup, find_packages

setup(
	name='simpleobserver',
	version='1.0.3',
	description='A very simple implementation of the observer pattern',
	long_description=io.open('README.rst', mode='r', encoding='utf-8').read(),
	classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Web Environment',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='events, patterns, observer',
    author='Elisha Fitch-Cook',
    author_email='elisha@cooper.com',
    url='http://github.com/cooper-software/observer',
    license='MIT',
    py_modules=['simpleobserver'],
    test_suite='test_simpleobserver'
)