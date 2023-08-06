# coding: utf-8
from setuptools import setup, find_packages
import sys, os
import recordpack

version = recordpack.__version__

setup(name='m3-recordpack',
      version=version,
      description=u'Пак общего назначения, для формирования и управления журнальными окнами и окнами справочников',
      long_description=open('README.rst').read(),
      author='Bars Group',
      author_email='bars@bars-open.ru',
      maintainer='Torsunov Andrey',
      maintainer_email='torsunov@bars-open.ru',
      keywords='django m3',
      classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
      ],
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      install_requires=[
          'm3-core',
          'm3-ui',
          'django'
      ],
)
