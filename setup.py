# coding=utf-8
from setuptools import setup, find_packages

__author__ = 'JeOam'

install_requires = [
    'Django>=1.9b1',
    'Markdown>=2.6',
]

setup(
    name='note4s',
    version='0.0.0',
    author='JeOam',
    author_email='249190843@qq.com',
    url='https://www.note4s.com',
    description='Note for sharing.',
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=install_requires,
)