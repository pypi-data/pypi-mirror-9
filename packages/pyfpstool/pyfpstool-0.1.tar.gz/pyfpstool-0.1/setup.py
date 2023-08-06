# coding: utf-8
import fps
from setuptools import setup, find_packages

setup(
    name='pyfpstool',
    version=fps.__version__,
    license="MIT",
    description='get fps rate tool',

    author='codeskyblue',
    author_email='codeskyblue@gmail.com',
    url='http://github.com/netease/unknown',

    py_modules=['pyfpstool'],
    install_requires=[
        'click >= 3.3',
        ],
    entry_points='''
        [console_scripts]
        fpstest = pyfpstool:main
    ''',
)
