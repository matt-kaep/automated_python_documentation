# Elevendoc: Automatic Docstring and README Generator for Python Projects

## Overview
Elevendoc is a Python package designed to automate the generation of docstrings for Python functions and create comprehensive README files for Python projects. It also provides an advisory file offering insightful advice on the project. This tool is particularly useful in the field of data science, where clear documentation and effective communication of project objectives and methodologies are crucial.

## About
Elevendoc is a Python package that automates the generation of docstrings for Python functions, creates a relevant README file, and provides an advisory file with project-specific advice. The primary features of this package include:

- Automatic generation of docstrings for Python functions.
- Creation of a comprehensive README file.
- Generation of an advisory file with project-specific advice.
- Reorganization of imports in the specified directory.
- Code formatting using the 'black' tool.

The project consists of the following files:

- `main.py`: This file contains the main functions of the project, including the creation of a .env file, the main function that performs various tasks based on the provided arguments, and the run function that serves as the entry point of the program.
- `utils.py`: This file contains utility functions that parse Python files, extract key elements, write docstrings to specified functions, interact with the AzureChatOpenAI model, reorganize imports, and visit nodes.
- `__init__.py`: This file indicates that the directory should be treated as a package.

## Directory Hierarchy
```
elevendoc/
│
├── main.py
├── utils.py
└── __init__.py
```

## Getting Started

### Prerequisites
Before you can run this project, you will need to have Python installed on your machine. You will also need to install the following Python libraries:

- ast
- black
- isort
- openai

You can install these libraries using pip:

```bash
pip install ast black isort openai
```

### Installation
To install the project, follow these steps:

1. Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/elevendoc.git
```

2. Navigate to the project directory:

```bash
cd elevendoc
```

### Running the Project
To run the project, use the following command:

```bash
python main.py --folder your_folder --docstring --Readme --advisory --force
```

Replace `your_folder` with the path to the folder containing the Python files you want to process.

## Usage
Here is an example of how to use the project:

```python
from elevendoc import main

main.run(folder='my_project', docstring=True, Readme=True, advisory=True, force=True)
```

This will generate docstrings for all Python functions in the 'my_project' directory, create a README file, generate an advisory file, and force the generation of docstrings even if they already exist.

## Technologies Used
- Python
- ast
- black
- isort
- openai

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Authors
- Matthieu Kaeppelin

## Acknowledgments
We would like to thank the open-source community for their continuous support and inspiration. Special thanks to the creators of the libraries used in this project.