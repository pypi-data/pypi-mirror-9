from setuptools import setup, find_packages


setup(name='coinop',
      version='0.1.3',
      description='Crypto-currency conveniences',
      url='http://github.com/GemHQ/coinop-py',
      author='Matt Smith',
      author_email='matt@gem.co',
      license='MIT',
      packages=find_packages(exclude=[
          u'*.tests', u'*.tests.*', u'tests.*', u'tests']),
      install_requires=[
          'PyNaCl==0.3.0',
          'cffi',
          'pytest',
          'pycrypto',
          'python-bitcoinlib',
          'pycoin==0.42',
          'PyYAML',
          'ecdsa'
      ],
      zip_safe=False)
