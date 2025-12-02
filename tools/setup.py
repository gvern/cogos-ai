from setuptools import setup, find_packages

setup(
    name="cogos",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
    ],
    python_requires=">=3.8",
) 