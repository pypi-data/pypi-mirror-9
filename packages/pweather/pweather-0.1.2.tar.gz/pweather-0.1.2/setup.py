#encoding:utf-8
from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='pweather',
      version=version,
      description="直接在终端查城市天气情况",
      long_description="""方便在终端查城市天气情况""",
      classifiers=[],  #Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python weather report terminal',
      author='zhaohf',
      author_email='zhaohuafei@gmail.com',
      url='https://github.com/laozhaokun/pweather',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'termcolor',
      ],
      entry_points={
        'console_scripts':[
            'pweather = src:main'
        ]
      },
)
