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

    # Set parameter values to command line supplied or defaults
    framerate = get_args_or_default("framerate", args, config)
    max_iterations = get_args_or_default("max_iterations", args, config)
    min_quality = get_args_or_default("min_quality", args, config)
    max_quality = get_args_or_default("max_quality", args, config)
    input_path = args.INPUT
    output_path = args.OUTPUT
    max_width = args.max_width
    max_height = args.max_height
    if max_width is None and max_height is None:
        max_width = get_args_or_default("max_width", args, config)
        max_height = get_args_or_default("max_height", args, config)

    # Rot an image
    rot(input_path,
        output_path,
        framerate,
        max_iterations,
        min_quality,
        max_quality,
        max_width,
        max_height)
    return

def get_args_or_default(varname, args, config):
    "Return value from args if specified, otherwise read defaults from config."
    if vars(args)[varname] is not None:
        return vars(args)[varname]
    else:
        return config["defaults"][varname]

if __name__ == "__main__":
    main()
