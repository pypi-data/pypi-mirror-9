#!/usr/bin/env python

from setuptools import setup, find_packages
from rainbow_django import VERSION

url="https://github.com/jeffkit/rainbow-django"

long_description="Rainbow Biz side Sdk for Django"

setup(name="rainbow-django",
      version=VERSION,
      description=long_description,
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url = url,
      long_description=long_description,
      packages=find_packages('.'),
      install_requires=[
	  'Django',
          'requests',
          ]
     )


