from setuptools import setup

setup(name='serdaripsum',
      version='1.1',
      description='serdar ipsum generator that runs on bash.',
      url='https://github.com/halilkaya/serdaripsum',
      author='Halil Kaya',
      author_email='kayahalil@gmail.com',
      license='GPLv3',
      scripts=['serdaripsum.py'],
      data_files=[('/opt/serdaripsum/', ['songs.txt'])],
      install_requires=['setuptools'],
      zip_safe=False)