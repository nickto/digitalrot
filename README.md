# Digitally rot an image
Save an image as JPEG multiple times.

Depending on the output it will either result in a final degraded image or a
video with the degradation process.

Interestingly enough, if we choose a single quality value for JPEG, it converges
to a stable image relatively quickly and additional degradation does not happen.
To avoid that we sample a quality value from a range (85 to 95 by default).

This project is inspired by [this](https://vk.com/putineveryday) art project.

## Dependencies

- ImageMagick
- ffmpeg
- Python 3

or

- Docker (with docker-compose)

## Usage
For help run
```
docker-compose run digitalrot --help
```

For example,
```
docker-compose run digitalrot -n 1000 -f 120 ./tests/assets/sample.jpeg ./test.mp4
```
Note that input and output can be specified only in the current directory. This
is because the output is generated in the docker and only the current directory
is mounted as volume using `docker-compose`.

## Sample image
Sample image (`./tests/assets/sample.jpeg`) has a Creative Commons license. The
original author is [UnB Agência](https://www.flickr.com/people/57913061@N04).
