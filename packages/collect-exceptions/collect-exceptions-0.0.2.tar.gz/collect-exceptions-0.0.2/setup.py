#!/usr/bin/env python

from setuptools import setup, find_packages
from collect_exceptions import VERSION

url = "https://github.com/Yemsheng/collect-exceptions"

long_description = "python exception collector"

setup(name="collect-exceptions",
      version=VERSION,
      description=long_description,
      maintainer="Yemsheng",
      maintainer_email="msheng.ye@foxmail.com",
      url=url,
      long_description=long_description,
      packages=find_packages('.'),
      zip_safe=False,
      install_requires=[]
      )
