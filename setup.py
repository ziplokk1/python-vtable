from setuptools import setup, find_packages

version = '0.1.0'

REQUIREMENTS = [
]

setup(
    name='python-vtable',
    version=version,
    packages=find_packages(),
    url='https://github.com/ziplokk1/python-vtable',
    license='LICENSE.txt',
    author='Mark Sanders',
    author_email='sdscdeveloper@gmail.com',
    install_requires=REQUIREMENTS,
    description='A simple 2D dictionary wrapper used to create a virtual table similar to excel in python.',
    include_package_data=True
)
