from setuptools import setup

setup(
    name='jsonmanager',
    version='0.2.3',
    author='Josh Matthias',
    author_email='jmatthias4570@gmail.com',
    packages=['jsonmanager', 'jsonmanager.validation_tools'],
    scripts=[],
    url='https://github.com/jmatthias/jsonmanager',
    license='LICENSE.txt',
    description=('Validation, coercion, and forms for JSON.'),
    long_description=open('README_pypi.txt').read(),
    install_requires=[
        ],
    )
