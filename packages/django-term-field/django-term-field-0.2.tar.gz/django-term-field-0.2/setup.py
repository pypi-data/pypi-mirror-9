# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


requirements = [
    'Django>=1.5',
]

tests_require = [
    ]

entry_points = {
    'console_scripts': [
    ],
}


setup(
    name='django-term-field',
    version='0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description='Django term field(with from-to multi value).',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    author='imagawa_yakata(oyakata)',
    author_email='imagawa.hougikumaru@gmail.com',
    url='https://bitbucket.org/imagawa_yakata/django-term-field',
    license='MIT',
    tests_require=tests_require,
    install_requires=requirements,
    entry_points=entry_points,
)
