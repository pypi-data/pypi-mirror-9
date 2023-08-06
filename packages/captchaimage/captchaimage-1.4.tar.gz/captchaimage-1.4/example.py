#!/usr/bin/python
#
# Usage: ./example.py [options] [word]
#
# Run this script to generate and display an image with any word of
# your choice.
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
    import Image
    import optparse
    import random
    parser = optparse.OptionParser(usage = "usage: %prog [options] [word]")
    parser.add_option("--font-face",
        default = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        dest = "font_face_path",
        help = "Path to the font face file to use. [default: %default]")
    parser.add_option("--font-size", default = 28,
        help = "Size of the font to use. [default: %default]", type = int)
    parser.add_option("--output", dest = "output_path",
        help = "Path of the image file to save. By default the image is "
        "displayed on screen and not permanently saved.")
    parser.add_option("--seed", default = 0, dest = "seed", help = "Random "
        "seed to use for distorting the text. [default: %default]", type = int)
    parser.add_option("--size-y", default = 32, dest = "size_y",
        help = "Height of the image file to create.", type = int)
    options, args = parser.parse_args()
    if len(args) > 1:
        parser.error("Unrecognized arguments")

    size_y = options.size_y
    image_data = captchaimage.create_image(
        options.font_face_path, options.font_size, size_y,
        "PYTHON" if len(args) < 1 else args[0], options.seed)
    image = Image.fromstring(
        "L", (len(image_data) / size_y, size_y), image_data)
    if options.output_path:
        image.save(options.output_path)
    else:
        image.show()
