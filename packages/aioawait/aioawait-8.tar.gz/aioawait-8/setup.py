"""
@author: Carlo Pires <carlopires@gmail.com>
"""
from setuptools import setup

def get_long_description():
    with open('README.rst') as readme:
        return readme.read()

setup(
    name='aioawait',
    version=8,
    url='https://bitbucket.org/carlopires/aioawait',
    author='Carlo Pires',
    author_email='carlopires@gmail.com',
    description="Call asynchronous functions of Python 3.4.3 asyncio infrastructure from synchronous code",
    long_description=get_long_description(),
    zip_safe=True,
    py_modules=['aioawait'],
    platforms='any',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
