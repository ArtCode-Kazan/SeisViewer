from setuptools import setup
from setuptools import find_packages

setup(name='SeisRevise',
      version='0.2.1ref',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mikkoartic@gmail.com',
      license='MIT',
      zip=False,
      install_requires=['numpy', 'matplotlib', 'scipy', 'peewee'])
