from setuptools import setup

setup(name='wppy',
      version='1.20',
      description='wppy is a tool to get the latest version of Wordpress and install and configure it for you in one-line command.',
      url='https://github.com/halilkaya/wppy',
      author='Halil Kaya',
      author_email='kayahalil@gmail.com',
      license='GPLv3',
      scripts=['wppy.py'],
      install_requires=['setuptools'],
      zip_safe=False)
