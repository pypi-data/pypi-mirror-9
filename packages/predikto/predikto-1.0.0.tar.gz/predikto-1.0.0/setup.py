import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='predikto',
    version='1.0.0',
    description='Predikto Python SDK',
    long_description=(read('README.rst')),
    author='Predikto, Inc.',
    license='ASL',
    packages=find_packages(exclude=['tests*', 'docs*']),
    author_email='rrusso@predikto.com',
    url='https://github.com/predikto/python-sdk',
    download_url='https://github.com/predikto/python-sdk/tarball/1.0.0',
    keywords=['predikto', 'analytics', 'predictive'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ]
)