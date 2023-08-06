try:
    from setuptools import setup, Extension
except ImportError :
    raise ImportError("setuptools module required, please go to https://pypi.python.org/pypi/setuptools and follow the instructions for installing setuptools")


setup(
    name='dedupe-variable-name',
    url='https://github.com/datamade/dedupe-variables-name',
    version='0.0.2',
    description='Name variable type for dedupe',
    packages=['dedupe.variables'],
    install_requires=['probablepeople', 'parseratorvariable', 'future'],
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php'
    )
