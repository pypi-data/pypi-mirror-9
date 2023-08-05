__author__ = 'simon'

from setuptools import setup,find_packages

setup(
    name='mydemon',
    version='1.0.0',
    url="http://www.douniu.la",
    license='MIT',
    author='simon',
    author_email='admin@douniu.la',
    description='simon test ',
    classifiers=[
        "Programming Language :: Python",
    ],
    platforms='any',
    keywords='framework testing',
    packages=find_packages(exclude=['test']),
    install_requires=[
        "tox"
    ]
)