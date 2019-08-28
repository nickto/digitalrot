import os
from digitalrot.rot import *
import subprocess
import re


SAMPLE_IMAGE = "tests/assets/sample.jpeg"

def test_file_md5():
    true_md5 = "012d76386a8fc732c4045de76de6c477"
    computed_md5 = file_md5(SAMPLE_IMAGE)
    assert computed_md5 == true_md5

def test_get_image_size():
    w, h = get_image_size(SAMPLE_IMAGE)
    assert (w, h) == (2000, 1333)

def test_get_new_image_size():
    w, h = get_new_image_size(100, 200, 100, 100)
    assert (w, h) == (50, 100)

    # Should be even
    w, h = get_new_image_size(100, 200, 100, 101)
    assert (w, h) == (50, 100)

    # No resizing is already small
    w, h = get_new_image_size(100, 200, 300, 400)
    assert (w, h) == (100, 200)

    # Only one specified
    w, h = get_new_image_size(100, 200, 100, None)
    assert (w, h) == (100, 200)

    w, h = get_new_image_size(100, 200, None, 100)
    assert (w, h) == (50, 100)

def test_resize_image(tmpdir):
    output = os.path.join(tmpdir, "output.jpeg")
    output = resize_image(SAMPLE_IMAGE, output, 100, 100)
    assert (100, 100) == get_image_size(output)

    # Upscale
    output = resize_image(output, output, 200, 300)
    assert (200, 300) == get_image_size(output)

def test_resave(tmpdir):
    output = os.path.join(tmpdir, "output.jpeg")
    output = resave(SAMPLE_IMAGE, output, 85, 95)
    assert os.path.exists(output)

def test_rot(tmpdir):
    def is_image(path):
        output = subprocess.check_output(
            ["file", path]).decode("utf-8")
        return len(re.findall(r"image", output, re.IGNORECASE)) > 0

    def is_media(path):
        output = subprocess.check_output(
            ["file", path]).decode("utf-8")
        return len(re.findall(r"media", output, re.IGNORECASE)) > 0


    # Image output
    output = os.path.join(tmpdir, "output.jpeg")

    out = rot(input_path=SAMPLE_IMAGE,
              output_path=output,
              max_iterations=4,
              min_quality=85,
              max_quality=95,
              framerate=None,
              max_width=480,
              max_height=320,
              verbose=False)
    assert os.path.exists(output)
    assert is_image(output)
    assert not is_media(output)

    # Video output
    output = os.path.join(tmpdir, "output.mp4")
    out = rot(input_path=SAMPLE_IMAGE,
              output_path=output,
              max_iterations=4,
              min_quality=85,
              max_quality=95,
              framerate=30,
              max_width=480,
              max_height=320,
              verbose=False)
    assert os.path.exists(output)
    assert not is_image(output)
    assert is_media(output)
