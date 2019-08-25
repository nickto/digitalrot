import os
import argparse
import subprocess
import re
import tempfile
import yaml
import math
import logging
from tqdm import tqdm
import hashlib
import random

def get_image_size(path):
    "Identify geometry using ImageMagick."
    description = subprocess.Popen(
        ["magick", "identify", "-verbose", path],
        stdout=subprocess.PIPE)
    output = subprocess.check_output(
        ["grep", "Geometry"],
        stdin=description.stdout)
    description.wait()

    output = output.decode("utf-8")
    width_regex = re.compile(r"(?<=\s)\d*(?=x)")
    height_regex = re.compile(r"(?<=x)\d*")
    width = int(width_regex.findall(output)[0])
    height = int(height_regex.findall(output)[0])

    return width, height

def get_new_image_size(height, width, config, args):
    "Get new image size, given max dimensions."
    if args.max_width is None and args.max_height is None:
        # Nothing is specified, read defaults
        max_width = config["defaults"]["max_width"]
        max_height = config["defaults"]["max_height"]
        scale_factor = min(max_width / width, max_height / height)
    elif args.max_width is None and args.max_height is not None:
        # Use only height
        scale_factor = args.max_height / height
    elif args.max_width is not None and args.max_height is None:
        # Use only width
        scale_factor = args.max_width / width
    elif args.max_width is not None and args.max_height is not None:
        # Use only width
        scale_factor = min(args.max_width / width, args.max_height / height)

    width = math.floor(scale_factor * width)
    height = math.floor(scale_factor * height)

    # ffmpeg requires both width and height to be even
    if width % 2 != 0:
        width -= 1
    if height % 2 != 0:
        height -= 1

    return width, height


def resize_image(input, output, width, height):
    "Resize image using ImageMagick."
    # \! is needed to ignore aspect ratio
    cmd = " ".join([
        "magick {:s}".format(input),
        "-resize {:d}x{:d}\!".format(width, height),
        "-quality {:d}".format(100),
        "{:s}".format(output)
    ])
    logging.debug("Executing " + cmd)
    subprocess.run(cmd, shell=True)
    logging.info("Resized, saved to {:s}".format(output))

    return output

def resave(input, output, min_quality, max_quality):
    """Resave image witg randomly sampled quality.

    Quality is sampled randomly in an interval to avoid early convergence."""
    filename, _ = os.path.splitext(input)
    png = filename + ".png"

    cmd = " ".join([
        "magick convert {:s}".format(input),
        "-colorspace {:s}".format("CMYK"),
        "+antialias",
        "-quality {:d}".format(100),
        "{:s}".format(png)
    ])
    logging.debug("Executing '{:s}' in shell".format(cmd))
    subprocess.run(cmd, shell=True)
    cmd = " ".join([
        "magick convert {:s}".format(png),
        "-colorspace {:s}".format("RGB"),
        "+antialias",
        "-quality {:d}".format(random.randint(min_quality, max_quality)),
        "{:s}".format(output)
    ])
    logging.debug("Executing '{:s}' in shell".format(cmd))
    subprocess.run(cmd, shell=True)
    logging.debug("Saved to {:s}".format(output))

    return output

def file_md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()
