#!/usr/bin/env python3
import os
import argparse
import subprocess
import re
import tempfile
import yaml
import math

def main():
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

    parser.add_argument("-q", "--qulaity",
        help="JPEG quaity to use for quality degradation (1-100)",
        default=None,
        metavar="N",
        dest="quality",
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
    temp_name_length = len(str(args.max_iterations))
    temp_name_format = "{{:0{:d}d}}".format(temp_name_length)

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = temp_dir.name

    # Resize image
    width, height = get_image_size(args.INPUT)
    input_path = args.INPUT
    output_name = temp_name_format.format(0) + ".jpeg"
    output_path = os.path.join(temp_path, output_name)
    width, height = get_new_image_size(height, width, config, args)
    print(width, height)






    #  temp_dir.cleanup()


    return

def get_image_size(path):
    # Identify geometry using ImageMagick
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
    if args.max_width is None and args.max_height is None:
        # Nothing is specified, read defaults
        max_width = config["defaults"]["max_width"]
        max_height = config["defaults"]["max_height"]
        scale_factor = min(max_width / width, max_height / height)
    elif args.max_width is None and args.max_height is not None:
        # Use only height
        scale_factor = max_height / height
    elif args.max_width is not None and args.max_height is None:
        # Use only width
        scale_factor = max_width / width
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


def resize_image(input, output):
    ""
    return



if __name__ == "__main__":
    main()
