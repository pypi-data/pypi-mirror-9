# coding: utf-8
import os
from setuptools import setup
import coinbase

README = open(os.path.join(os.path.dirname(__file__), 'PYPIREADME.rst')).read()
REQUIREMENTS = [
    line.strip() for line in open(os.path.join(os.path.dirname(__file__),
                                               'requirements.txt')).readlines()]

setup(
    name='coinbase',
    version=coinbase.__version__,
    packages=['coinbase'],
    include_package_data=True,
    license='MIT License',
    description='Coinbase API client library',
    long_description=README,
    url='https://github.com/coinbase/coinbase-python/',
    download_url='https://github.com/coinbase/coinbase-python/tarball/%s' % (
      coinbase.__version__),
    keywords=['api', 'coinbase', 'bitcoin', 'oauth2', 'client'],
    install_requires=REQUIREMENTS,
    author='Coinbase, Inc.',
    author_email='api@coinbase.com',
    classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
