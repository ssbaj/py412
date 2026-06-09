from setuptools import setup, find_packages

setup(
    name="py412",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
        "chardet",
        "pyreadstat",
    ],
    python_requires=">=3.8",
)