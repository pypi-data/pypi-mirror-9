import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(name='cleveland',
      version='0.1',
      author='John Biesnecker',
      author_email='jbiesnecker@gmail.com',
      url='https://github.com/biesnecker/cleveland',
      packages=['cleveland'],
      package_dir={'cleveland': './cleveland'},
      #package_data={'reverse_geocoder': ['rg_cities1000.csv']},
      description='Simple asyncio-based actors.',
      license='mit',
      long_description=read('README.txt')
)