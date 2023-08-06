#!/usr/bin/python
#
# python-captchaimage
#
# 2008, 2015 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

from distutils.core import setup, Extension
setup(
    name = "captchaimage",
    version = "1.4",
    author = "Fredrik Portstrom",
    author_email = "https://portstrom.com",
    url = "https://portstrom.com",
    description = "Create captcha image data",
    long_description = "python-captchaimage is a fast and easy to use Python "
    "extension for creating images with distorted text that are easy for "
    "humans and difficult for computers to read. Glyphs are loaded as bezier "
    "curves using Freetype, rotated and scaled randomly, and then distorted by "
    "adding Perlin noise to each point of the curve before rendering into a "
    "bitmap.",
    license = "Public Domain",
    classifiers = [
        "License :: Public Domain",
        "Programming Language :: C"],
    ext_modules = [Extension(
            "captchaimage", ["captchaimage.c"],
            include_dirs = ["/usr/include/freetype2"],
            libraries = ["freetype"])])
