from setuptools import setup, find_packages

setup(
    name="Backgroundr",

    keywords="Backgrounds Wallpapers Images",

    version="1.1.7",

    install_requires=[
        "Pillow",
    ],

    packages=find_packages(),

    package_data={
        'fonts': ['backgroundr/fonts/*']
    },

    include_package_data=True,

    url="https://github.com/smg247/backgroundr",

    author="Stephen Goeddel",

    author_email="stephen@stephengoeddel.com"

)
