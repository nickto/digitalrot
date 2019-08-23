#!/usr/bin/env python3
import os
import argparse
import subprocess
import re

def main():
    parser = argparse.ArgumentParser(description='Digitally rot an image.')
    
    parser.add_argument("INPUT",
            help="input file")

    parser.add_argument("OUTPUT",
            help="output file, output type is inferred from extension")

    parser.add_argument("-n", "--number",
            help="max number of iterations",
            default=100,
            metavar="N",
            dest="max_iterations",
            required=False,
            type=int)

    parser.add_argument("--width",
            help="max width of the resulting image",
            default=480,
            metavar="PIXELS",
            dest="max_width",
            required=False,
            type=int)

    parser.add_argument("--height",
            help="max height of the resulting image",
            default=320,
            metavar="PIXELS",
            dest="max_height",
            required=False,
            type=int)

    parser.add_argument("-q", "--qulaity",
            help="JPEG quaity to use for quality degradation (1-100)",
            default=95,
            metavar="N",
            dest="quality",
            required=False,
            type=int)
    
    parser.add_argument("-f", "--framerate",
            help="video framerate (ignored it output is a static image",
            default=30,
            metavar="N",
            dest="framerate",
            required=False,
            type=int)

    args = parser.parse_args()

    width, height = get_image_size(args.INPUT)
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


if __name__ == "__main__":
    main()