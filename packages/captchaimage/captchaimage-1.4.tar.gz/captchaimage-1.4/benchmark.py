#!/usr/bin/python
#
# Usage: ./benchmark.py
#
# Run this script to see how captchaimage performs on your computer.
#
# 2008, 2015 Fredrik Portstrom <https://portstrom.com>
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

try:
    import captchaimage
except ImportError:
    print "The captchaimage module is not installed."
else:
    import timeit
    number = 1000
    timer = timeit.Timer(
        "create_image('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', 30, "
        "32, 'EMACS')", "from captchaimage import create_image")
    for i in xrange(5):
        time = timer.timeit(number = number)
        print "Generated %d captcha images in %.2f seconds. That is %.2f " \
            "images per second." % (number, time, number / time)
