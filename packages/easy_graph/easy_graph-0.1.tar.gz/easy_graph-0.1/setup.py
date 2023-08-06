from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='easy_graph',
      version=version,
      description="Easily turn your python data into a flot graph in a static html file.",
      long_description="""""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='graph graphing plot',
      author='Jesse Aldridge',
      author_email='JesseAldridge@gmail.com',
      url='https://github.com/JesseAldridge/easy_graph',
      license='MIT',
      packages=['easy_graph'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
