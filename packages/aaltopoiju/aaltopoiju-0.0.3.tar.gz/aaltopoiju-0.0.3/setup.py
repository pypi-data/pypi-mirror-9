from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aaltopoiju',
    version='0.0.3',
    description='Screen scraper for aaltopoiju.fi',
    long_description=long_description,
    url='https://github.com/ojarva/python-aaltopoiju',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2.7',
    ],
    keywords='aaltopoiju',
    packages=["aaltopoiju"],
    install_requires=["requests", "beautifulsoup4"],
    test_suite="tests",

    extras_require = {
        'dev': ['twine', 'wheel'],
    },
)
