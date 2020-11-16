from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["ipython>=6", "requests>=2"]

setup(
    name="geo_utils",
    version="0.0.1",
    author="Sebastian Schwindt",
    author_email="sebastian.schwindt@iws.uni-stuttgart.de",
    description="Geo utils",
    long_description=readme,
    long_description_content_type="README.md",
    url="https://github.com/hydro-informatics/geo-utils",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)