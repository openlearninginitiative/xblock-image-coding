"""Setup for image-coding xblock"""

import os
from setuptools import setup


def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='xblock-image-coding',
    version='0.3',
    description='Image Coding XBlock',
    packages=[
        'image_coding',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'image-coding = image_coding:ImageCodingXBlock',
        ]
    },
    package_data=package_data("image_coding", "static"),
)