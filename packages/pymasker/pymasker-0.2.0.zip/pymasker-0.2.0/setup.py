from setuptools import setup

setup(name='pymasker',
      version='0.2.0',
      description='python package for mask generation from landsat 8 Quality Assessment band and MODIS land products.',
      url='https://github.com/dz316424/pymasker',
      author='Haoliang Yu',
      author_email='njkon@foxmail.com',
      license='Apache',
      packages=['pymasker'],
      install_requires=['numpy',],
      zip_safe=False)