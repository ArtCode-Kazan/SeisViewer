from setuptools import setup
from setuptools import find_packages

setup(name='SeisRevise',
      version='1.1.3',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      include_package_data=True,
      zip=False
      )
