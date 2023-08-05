#! /usr/bin/python
from distutils.core import setup
from glob import glob

# to install type:
# python setup.py install --root=/

setup (name='PyArabic', version='0.5',
      author='Taha Zerrouki',
      author_email='taha_zerrouki@hotmail.com',
      url='http://pyarabic.sourceforge.net/',
      license='GPL',
      description="Arabic Arabic text tools for Python",
      Platform="OS independent",
      package_dir={'pyarabic': 'pyarabic',},
      packages=['pyarabic'],
      # include_package_data=True,
      package_data = {
        'pyarabic': ['doc/*.*','doc/html/*'],
        },
      classifiers=[
          'Development Status :: 5 - Beta',
          'Intended Audience :: End Users/Desktop',
          'Operating System :: OS independent',
          'Programming Language :: Python',
          ],
    );

