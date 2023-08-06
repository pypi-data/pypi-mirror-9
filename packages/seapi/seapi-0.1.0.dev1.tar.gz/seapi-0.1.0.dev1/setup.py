from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from os import path

setup(
    name='seapi',

    version='0.1.0.dev1',

    description='a python library to query SiliconExpert API to gain information about electronic components and manufacturers/suppliers',

    url='https://github.com/biwa7636/seapi',

    author='Gayatri Ghanakota, Richard Rymer, Bin Wang',
    author_email='binwang.cu@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='api siliconexpert components',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['oauth2'],

    entry_points={
        'console_scripts': [
            'seapi=seapi:main',
        ],
    },
)
