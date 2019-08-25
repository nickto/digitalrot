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
from digitalrot.rot import *

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

if __name__ == "__main__":
    main()
