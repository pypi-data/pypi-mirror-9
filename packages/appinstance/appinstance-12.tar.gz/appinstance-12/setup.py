# coding=utf-8
"""
appinstance
Active8 (04-03-15)
license: GNU-GPL2
"""
from setuptools import setup
setup(name='appinstance',
      version='12',
      description='Check if an app with the same name is running, supports parameters.',
      url='https://github.com/erikdejonge/appinstance',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      packages=['appinstance'],
      zip_safe=True,
      install_requires=['psutil'])
