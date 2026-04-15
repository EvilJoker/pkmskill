from setuptools import setup, find_packages

setup(
    name="pkm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.7",
        "requests>=2.31.0",
        "apscheduler>=3.10.0",
    ],
    entry_points={
        "console_scripts": [
            "pkm=pkm.cli:cli",
        ],
    },
)
