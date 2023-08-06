"""Setup."""

from setuptools import setup


setup(
    name='txmandrill',
    version='1.0.0',
    description='The Mandrill Python client but for Twisted..',
    author='Lex Toumbourou',
    author_email='lextoumbourou@gmail.com',
    url='https://github.com/lextoumbourou/txmandrill-api',
    license='Apache',
    py_modules=['txmandrill'],
    install_requires=[
        'mandrill==1.0.57', 'Twisted', 'zope.interface',
        'treq', 'service_identity'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
