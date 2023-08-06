# -*- coding: utf-8 -*-

import os

from setuptools import setup


__here__ = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(__here__, 'README.rst')).read()
REQUIREMENTS = [
    i.strip()
    for i in open(os.path.join(__here__, 'requirements.txt')).readlines()
]

# Get VERSION
version_file = os.path.join('txinvoke', 'version.py')
# Use exec for compabibility with Python 3
exec(open(version_file).read())


setup(
    name='txinvoke',
    version=VERSION,
    description="Run inline callbacks from Twisted as Invoke tasks",
    long_description=README,
    keywords=[
        'twisted', 'invoke', 'task', 'callback', 'deferred', 'asynchronous',
    ],
    license='MIT',
    url='https://github.com/oblalex/txinvoke',
    author='Alexander Oblovatniy',
    author_email='oblovatniy@gmail.com',
    packages=[
        'txinvoke',
    ],
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Framework :: Twisted',
    ],
    platforms=[
        'any',
    ],
)
