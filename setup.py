from setuptools import setup, find_packages

setup(
    name="muli",
    version="0.1",
    install_requires=[
        "tqdm",
        "docstring_parser",
    ],
    author="h-terao",
    packages=find_packages(),
)
