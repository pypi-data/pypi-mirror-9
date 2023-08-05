# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


requirements = [
    'requests',
    'paramiko',
    'pyyaml',
    'flake8',
    'jinja2',
]

tests_require = [
    ]

entry_points = {
    'console_scripts': [
        'publickey=publickey:main',
    ],
}


setup(
    name='publickey',
    version='0.3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description='Control downloading/uploading publickeys.',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    author='imagawa_yakata(oyakata)',
    author_email='imagawa.hougikumaru@gmail.com',
    url='https://bitbucket.org/imagawa_yakata/publickey',
    license='MIT',
    tests_require=tests_require,
    install_requires=requirements,
    entry_points=entry_points,
)
