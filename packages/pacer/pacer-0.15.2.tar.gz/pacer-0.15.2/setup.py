# encoding: utf-8

PKG_NAME = 'pacer'
VERSION = (0, 15, 2)
AUTHOR = 'Uwe Schmitt'
AUTHOR_EMAIL = 'uwe.schmitt@id.ethz.ch'
AUTHOR_URL = 'https://ssdmsource.ethz.ch/sis/pacer/tree/master'

DESCRIPTION = ("pacer is a lightweight Python package for implementing distributed data "
               "processing workflows.")

LICENSE = "http://opensource.org/licenses/GPL-3.0"

import os.path
LONG_DESCRIPTION = ""
if os.path.exists("_README.rst"):
    LONG_DESCRIPTION = open("_README.rst", "r").read()


if __name__ == "__main__":   # allows import setup.py for version checking

    from setuptools import setup
    setup(name=PKG_NAME,
          packages=[PKG_NAME],
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=AUTHOR_URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          version="%s.%s.%s" % VERSION,
          install_requires = ["dill", "tblib"],
          zip_safe=False,
          )
