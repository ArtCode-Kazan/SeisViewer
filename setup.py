from setuptools import setup
from setuptools import find_packages


setup(name='seisviewer',
      version='2.2.6',
      packages=find_packages(),
      description='Package for processing of microseismic data',
      author='Michael Chernov',
      author_email='mihail.tchernov@yandex.ru',
      license='MIT',
      include_package_data=True,
      zip_safe=False,
      package_data={'seisviewer': ['gui/forms/*.ui']}
      )
