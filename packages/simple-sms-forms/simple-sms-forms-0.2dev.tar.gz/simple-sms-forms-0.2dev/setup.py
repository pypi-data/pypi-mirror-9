from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='simple-sms-forms',
      version=version,
      description="Simple SMS text processor for Django/Rapidsms",
      long_description="""\
A small package to help in parsing simple text messages to come up with ordered data. Aimed at RapidSMS""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='RapidSMS, SMS, Django',
      author='Andre Lesa',
      author_email='andre@andrelesa.com',
      url='https://github.com/AndreLesa/simplesmsforms',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
