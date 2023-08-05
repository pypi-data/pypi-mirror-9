from os import walk, path
from setuptools import setup, find_packages

setup(
    name="Backgroundr",

    keywords="Backgrounds Wallpapers Images",

    version="1.1.1",

    install_requires=[
        "Pillow",
    ],

    packages=find_packages(),

    data_files=[
        (root, [path.join(root, f) for f in files])
        for root, dirs, files in walk('fonts')
    ],

    url="https://github.com/smg247/backgroundr",

    author="Stephen Goeddel",

    author_email="stephen@stephengoeddel.com"

)
