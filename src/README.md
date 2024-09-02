# Python Docstring and README Generator

This project is a Python-based utility that automates the generation of docstrings and README files for Python projects. It also has the capability to generate advisory files. The project is designed to help developers save time and maintain consistency in their documentation.

## About

The project consists of two main Python files: `main1.py` and `utils1.py`.

`main1.py` contains the main function that performs various tasks based on the provided arguments. It can generate and add docstrings to Python files, generate README files, and generate advisory files in the specified directory.

`utils1.py` contains several utility functions that are used by the main function. These include functions to extract function definitions from a Python file, extract key elements from a Python file, write changes to a Python file, and send code to ChatGPT for completion.

## Getting Started

To get this project up and running on your local machine, follow the instructions below.

### Prerequisites

You will need the following software installed on your machine:

- Python 3.6 or higher
- pip (Python package installer)

### Installing

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### Running the project

To run the project, navigate to the project directory and run the following command:

```bash
python main1.py --docstring --Readme --advisory <your_directory>
```

Replace `<your_directory>` with the directory where you want the project to perform its tasks.



This command will generate and add docstrings to all Python files in the `./my_project` directory.

## Built Using

- Python
- ast (Python's Abstract Syntax Trees module)
- OpenAI's ChatGPT

## Contributing

If you would like to contribute to this project, please fork the repository, make your changes, and submit a pull request.

## Authors

- Matthieu Kaeppelin

## Acknowledgments

- OpenAI for their ChatGPT model
- Python's ast module
