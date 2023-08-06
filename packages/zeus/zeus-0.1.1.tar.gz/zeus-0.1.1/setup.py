#!/usr/bin/env python
from distutils.core import setup


setup(name="zeus",
      version="0.1.1",
      description="HTML templating DSL",
      author="Dmitry Veselov",
      author_email="d.a.veselov@yandex.ru",
      url="https://github.com/dveselov/zeus",
      py_modules=["zeus"],
      scripts=["zeus.py"],
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: MIT License",

          "Programming Language :: Python :: 3.4",

          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
      ],
     )
