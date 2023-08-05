PKG_NAME = 'presettr'
VERSION = (0, 5, 0)
AUTHOR = 'Uwe Schmitt'
AUTHOR_EMAIL = 'uwe.schmitt@id.ethz.ch'
AUTHOR_URL = 'https://ssdmsource.ethz.ch/sis/pacer/tree/master'

DESCRIPTION = ("presettr is a layer above guidata for simplified und reusable parameter handling")

LICENSE = "http://opensource.org/licenses/GPL-3.0"

import os.path
LONG_DESCRIPTION = ""
if os.path.exists("_README.rst"):
    LONG_DESCRIPTION = open("_README.rst", "r").read()


if __name__ == "__main__":

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
          zip_safe=False,
          install_requires = ["guidata"],
          )
