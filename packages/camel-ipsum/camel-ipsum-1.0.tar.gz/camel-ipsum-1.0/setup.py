from setuptools import setup

setup(name='camel-ipsum',
      version='1.0',
      description='camel ipsum generator that runs on bash.',
      url='https://github.com/camelware/camel-ipsum',
      author='Camel Soft',
      author_email='kayahalil@gmail.com',
      license='GPLv3',
      scripts=['camelipsum.py'],
      install_requires=['setuptools'],
      zip_safe=False)