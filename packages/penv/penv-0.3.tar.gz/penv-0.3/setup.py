# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup, find_packages


version = re.search(
    r"VERSION = ['\"](.*)['\"]",
    io.open('penv/__init__.py').read()
).group(1)


setup(
    name='penv',
    version=version,
    description='Framework for ease project management tools building.',
    author='Jakub Janoszek',
    author_email='kuba.janoszek@gmail.com',
    include_package_data=True,
    url='https://github.com/jqb/penv/tree/ver-%s' % version,
    packages=find_packages(),
    install_requires=[
        "click==3.3",
    ],
    entry_points=io.open('entry-points.ini', 'r').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)

# Usage of setup.py:
# $> python setup.py register                         # registering package on PYPI
# $> python setup.py build sdist bdist_wheel upload   # build, make source dist and upload to PYPI
