# CVPR Explorer

A simple set of Python scripts that can be used to download and explore CVPR publications.

Python 3 and Pip are required for use of this project.

## Using this Project

Functionality is split into two main files: `compile.py` and `explorer.py`

`compile.py` compiles a list of publications from a specific CVPR year into a JSON "library" for later exploration.

`explorer.py` enables exploration of a compiled library through use of keywords.

Instructions for use are detailed below.

### Prerequisites

Clone the project to a directory of your choosing, navigate to the directory in your shell of choice, and install the dependencies for this project with Pip:

```bash
pip install -r requirements.txt
```

### Compiling a Library

Run `compile.py` using Python and specify the CVPR year you wish to scrape as the first argument. To view other optional CLI arguments, use the `-h` argument.

```bash
# The below will compile all CVPR 2021 publications into a library
python compile.py 2021
```

Libraries are stored as JSON files in the current working directory within a created `libraries` folder.

### Exploring a Library

Run `explorer.py` using Python to start the process of exploring a given library (or a set of libraries). A small guide will walk you through the available options for sorting/exploring the available publications. `explorer.py` will look for a `libraries` folder in your current working directory.

```bash
python compile.py
```

## License

MIT
