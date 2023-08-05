from setuptools import setup, find_packages

setup(
    name="Backgroundr",

    keywords="Backgrounds Wallpapers Images",
    
    description="A simple way to create backgrounds for your computer with custom colors and text",

    version="1.1.10",

    install_requires=[
        "Pillow",
    ],

    packages=find_packages(),

    package_data={
        "fonts": ["fonts/*"]
    },

    include_package_data=True,

    url="https://github.com/smg247/backgroundr",

    author="Stephen Goeddel",

    author_email="stephen@stephengoeddel.com"

)
