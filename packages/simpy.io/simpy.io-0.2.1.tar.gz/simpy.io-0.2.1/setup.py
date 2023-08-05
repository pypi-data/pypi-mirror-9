# encoding: utf-8
from setuptools import setup, find_packages


setup(
    name='simpy.io',
    version='0.2.1',
    author='Ontje Lünsdorf',
    author_email='oluensdorf at gmail.com',
    description='Asynchronous networking based on SimPy.',
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    url='https://bitbucket.org/simpy/simpy.io',
    license='MIT License',
    install_requires=[
        'SimPy>=3',
    ],
    packages=['simpy.io'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Networking',
    ],
)
