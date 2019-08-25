#!/usr/bin/env python3
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

def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Digitally rot an image.')

    parser.add_argument("INPUT",
        help="input file")

    parser.add_argument("OUTPUT",
        help="output file, output type is inferred from extension")

    parser.add_argument("-n", "--number",
        help="max number of iterations",
        default=None,
        metavar="N",
        dest="max_iterations",
        required=False,
        type=int)

    parser.add_argument("--width",
        help="max width of the resulting image",
        default=None,
        metavar="PIXELS",
        dest="max_width",
        required=False,
        type=int)

    parser.add_argument("--height",
        help="max height of the resulting image",
        default=None,
        metavar="PIXELS",
        dest="max_height",
        required=False,
        type=int)

    parser.add_argument("-minq", "--min-quality",
        help="min JPEG quaity to use for quality degradation (1-100)",
        default=None,
        metavar="N",
        dest="min_quality",
        required=False,
        type=int)

    parser.add_argument("-maxq", "--max-quality",
        help="max JPEG quaity to use for quality degradation (1-100)",
        default=None,
        metavar="N",
        dest="max_quality",
        required=False,
        type=int)

    parser.add_argument("-f", "--framerate",
        help="video framerate (ignored it output is a static image",
        default=None,
        metavar="N",
        dest="framerate",
        required=False,
        type=int)

    # Parse arguments
    args = parser.parse_args()

    # Read in configs
    with open("./config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Create temporary directory and compute all the data needed for temporary
    # output
    max_iterations = get_args_or_default("max_iterations", args, config)
    temp_name_length = len(str(max_iterations))
    temp_name_format = "{{:0{:d}d}}".format(temp_name_length)

    with tempfile.TemporaryDirectory() as temp_path:
        assert os.path.isdir(temp_path)

        # Resize image
        width, height = get_image_size(args.INPUT)
        logging.info("Input image dimensions are {:d} × {:d}".format(width,
                                                                     height))
        width, height = get_new_image_size(height, width, config, args)
        logging.info("Image will be scaled to {:d} × {:d}".format(width,
                                                                  height))

        input_path = args.INPUT
        output_name = temp_name_format.format(0) + ".jpeg"
        output_path = os.path.join(temp_path, output_name)
        output_path = resize_image(input_path, output_path, width, height)
        output_md5 = file_md5(output_path)

        # Start resaving
        min_quality = get_args_or_default("min_quality", args, config)
        max_quality = get_args_or_default("max_quality", args, config)
        max_iterations = get_args_or_default("max_iterations", args, config)
        for i in tqdm(range(max_iterations)):
            input_path = output_path
            input_md5 = output_md5

            output_path = os.path.join(
                temp_path,
                temp_name_format.format(i) + ".jpeg")
            output = resave(input_path, output_path, min_quality, max_quality)
            output_md5 = file_md5(output_path)

            if input_md5 == output_md5:
                logging.info("Early stop at iteration {:d}".format(i))
                break

        # Video or image?
        _, extension = os.path.splitext(args.OUTPUT)
        extension = extension[1:]  # strip leading dot
        if extension.lower() in ["jpeg", "jpg", "png", "bmp", "tiff", "tif"]:
            # Image
            logging.info("Otput extension '{:s}', hence outputting image".format(extension))
            resave(output, args.OUTPUT, 100, 100)
        else:


            # Video
            logging.info("Otput extension '{:s}', hence outputting video".format(extension))
            framerate = get_args_or_default("framerate", args, config)
            cmd = " ".join([
                "ffmpeg",
                "-framerate {:d}".format(framerate),
                "-f image2",
                "-i {:s}".format(os.path.join(temp_path, "%0{:d}d.jpeg".format(temp_name_length))),
                "-y",
                "{:s}".format(args.OUTPUT)
            ])
            logging.info("Executing '{:s}' in shell".format(cmd))
            subprocess.run(cmd, shell=True)
    return

def get_args_or_default(varname, args, config):
    if vars(args)[varname] is not None:
        return vars(args)[varname]
    else:
        return config["defaults"][varname]

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
    "Resave image witg randomly sampled quality."
    filename, _ = os.path.splitext(input)
    png = filename + ".png"

    cmd = " ".join([
        "magick convert {:s}".format(input),
        # "-fill {:s} -draw 'point {:d},{:d}'".format("white" if random.random() > 0.5 else "black", 1, 1),
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

if __name__ == "__main__":
    main()
