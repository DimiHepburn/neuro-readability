"""
setup.py
~~~~~~~~
Install neuro-readability as a Python package with the 'nr' CLI command.

    pip install -e .          # install in editable/dev mode
    pip install .             # standard install
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="neuro-readability",
    version="1.0.0",
    author="Dimitri (DimiHepburn)",
    author_email="",
    description=(
        "A neuroscience-informed Python CLI tool that analyses text "
        "for cognitive load, readability, and complexity."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DimiHepburn/neuro-readability",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
    ],
    extras_require={
        "accurate-syllables": ["nltk>=3.7"],
    },
    entry_points={
        "console_scripts": [
            "nr=cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    keywords=[
        "readability", "nlp", "text-analysis", "cognitive-load",
        "flesch-kincaid", "neuroscience", "cli", "writing-tools"
    ],
)
