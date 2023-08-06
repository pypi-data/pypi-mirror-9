# coding: utf-8
import pyfpstool
from setuptools import setup, find_packages

setup(
    name='pyfpstool',
    version=pyfpstool.__version__,
    license="MIT",
    description='get fps rate tool',

    author='codeskyblue',
    author_email='codeskyblue@gmail.com',
    url='http://github.com/netease/unknown',

    packages = find_packages(),
    include_package_data=True,
    package_data={},
    install_requires=[
        'click >= 3.3',
        ],
    entry_points='''
        [console_scripts]
        fpstool = pyfpstool:main
    ''',
)
