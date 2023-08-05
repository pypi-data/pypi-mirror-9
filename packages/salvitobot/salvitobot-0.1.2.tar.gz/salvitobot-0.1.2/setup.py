# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'dataset',
    'python-wordpress-xmlrpc',
    'requests',
    'feedparser',
    'requests_oauthlib',
    'pytz',
    'arrow',
]

test_requirements = [
    'pep8',
    'coverage',
    'nose',
    'Sphinx',
    'coveralls',
]

setup(
    name="salvitobot",
    version="0.1.2",
    url="https://github.com/aniversarioperu/salvitobot",

    author="AniversarioPeru",
    author_email="aniversarioperu1@gmail.com", maintainer="AniversarioPeru",
    maintainer_email="aniversarioperu1@gmail.com",

    description="avisa sismos y tsunamis",
    long_description=open('README.rst').read(),

    packages=[
        'salvitobot',
    ],
    package_dir={'salvitobot':
                 'salvitobot'},
    include_package_data=True,
    install_requires=requirements,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',

        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
