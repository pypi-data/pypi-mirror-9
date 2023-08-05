from setuptools import setup


setup(
    name='simplio',
    version='0.1.1',
    description='Simplest-case command-line input/output',
    long_description=(
        'Simplio is a Python function decorator that applies an input file '
        'object and an output file object as arguments to the decorated '
        'function. It determines this based on STDIN or the presence of '
        'command-line arguments.'),
    url='https://github.com/josephl/simplio',
    author='Joseph Lee',
    author_email='joe.lee.three.thousand@gmail.com',
    license='MIT',
    keywords='input output file io',
    packages=['simplio'],
)
