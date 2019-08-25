import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="digitalrot",
    version="0.0.9000",
    author="Nick To",
    author_email="nickto0x64@gmail.com",
    description="Digitally rot an image",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nickto/digitalrot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
