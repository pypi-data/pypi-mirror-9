# coding=utf8
from setuptools import setup, find_packages


setup(
    name="bluelake",
    version="1.0.1",
    description="Bluelake python client.",
    author="Eleme BPM",
    author_email="bpm@ele.me",
    packages=find_packages(),
    zip_safe=False,
    # entry_points={"console_scripts": entry_points},
    install_requires=["requests==2.5.3"]
)
