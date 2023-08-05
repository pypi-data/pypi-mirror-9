from setuptools import setup

VERSION = '3.0.0-alpha10'

setup(
    name="Ferris",
    version=VERSION,
    author='Jon Parrott / Cloud Sherpas',
    author_email='jjramone13@gmail.com',
    maintainer='Jon Parrott / Cloud Sherpas',
    maintainer_email='jonathan.parrott@cloudsherpas.com',
    description='A framework for creating APIs on Google App Engine',
    url='https://bitbucket.org/cloudsherpas/ferris3',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    packages=['ferris3'],
    install_requires=[
        'google-api-python-client',
        'protopigeon'
    ],
)
