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

def rot(input_path, output_path, framerate, max_iterations, min_quality, max_quality, max_width=None, max_height=None):
    # Create temporary directory and compute all the data needed for temporary
    # output
    temp_name_length = len(str(max_iterations))
    temp_name_format = "{{:0{:d}d}}".format(temp_name_length)

    with tempfile.TemporaryDirectory() as temp_path:
        assert os.path.isdir(temp_path)

        # Resize image
        width, height = get_image_size(input_path)
        logging.info("Input image dimensions are {:d} × {:d}".format(width,
                                                                     height))
        width, height = get_new_image_size(width, height, max_width, max_height)
        logging.info("Image will be scaled to {:d} × {:d}".format(width,
                                                                  height))

        output_name = temp_name_format.format(0) + ".jpeg"
        temp_output_path = os.path.join(temp_path, output_name)
        temp_output_path = resize_image(input_path, temp_output_path, max_width, max_height)
        output_md5 = file_md5(temp_output_path)

        # Start resaving
        for i in tqdm(range(max_iterations)):
            input_path = temp_output_path
            input_md5 = output_md5

            temp_output_path = os.path.join(
                temp_path,
                temp_name_format.format(i) + ".jpeg")
            output = resave(input_path, temp_output_path, min_quality, max_quality)
            output_md5 = file_md5(temp_output_path)

            if input_md5 == output_md5:
                logging.info("Early stop at iteration {:d}".format(i))
                break

        # Video or image?
        _, extension = os.path.splitext(output_path)
        extension = extension[1:]  # strip leading dot
        if extension.lower() in ["jpeg", "jpg", "png", "bmp", "tiff", "tif"]:
            # Image
            logging.info("Otput extension '{:s}', hence outputting image".format(extension))
            resave(output, output_path, 100, 100)
        else:


            # Video
            logging.info("Otput extension '{:s}', hence outputting video".format(extension))
            cmd = " ".join([
                "ffmpeg",
                "-framerate {:d}".format(framerate),
                "-f image2",
                "-i {:s}".format(os.path.join(temp_path, "%0{:d}d.jpeg".format(temp_name_length))),
                "-y",
                "{:s}".format(output_path)
            ])
            logging.info("Executing '{:s}' in shell".format(cmd))
            subprocess.run(cmd, shell=True)

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

def get_new_image_size(width, height, max_width=None, max_height=None):
    "Get new image size, given max dimensions."
    if max_width is None and max_height is None:
        raise Exception("Either max_width or max_height (or both) should be specified.")
    elif max_width is None and max_height is not None:
        # Use only height
        scale_factor = max_height / height
    elif max_width is not None and max_height is None:
        # Use only width
        scale_factor = max_width / width
    elif max_width is not None and max_height is not None:
        # Use only width
        scale_factor = min(max_width / width, max_height / height)

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
