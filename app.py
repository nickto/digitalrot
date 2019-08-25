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

    rot(args)
    return

if __name__ == "__main__":
    main()
