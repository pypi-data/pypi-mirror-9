import os
from setuptools import setup, find_packages


setup(name="static-future",
      version="0.0.2",
      author="Ellis Percival",
      author_email="static-future@failcode.co.uk",
      description="Static analysis tool to establish which __future__ imports "
                  "are used in python source code.",
      license="UNLICENSE",
      keywords="future __future__ static analysis python source code",
      url="https://github.com/flyte/static-future",
      packages=("static_future",))
