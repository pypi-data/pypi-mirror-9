'''
Created on Dec 29, 2014

@author: jordan
'''
from setuptools import setup

setup(name='autotag',
      version='0.38',
      description='Tag suggestion according to text ',
      url='https://github.com/jvalansi/autotag',
      author='Jordan Valansi',
      author_email='jvalansi_autotag@gmail.com',
      license='MIT',
      packages=['autotag'],
      install_requires=[
          'nltk==3',
      ],
      zip_safe=False)
