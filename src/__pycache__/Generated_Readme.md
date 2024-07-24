# Python Code Documentation Generator

This project is a Python code documentation generator that uses OpenAI's GPT-3 model to generate docstrings, README files, and advisory files for Python code. It is designed to help developers automate the process of documenting their code.

## About

The project consists of two main Python files: `main.py` and `utils.py`. 

`main.py` is the main script that processes Python files in a directory and generates docstrings, README, or advisory based on the arguments provided. It uses the `os` and `argparse` libraries to navigate the file system and parse command line arguments, respectively.

`utils.py` contains the function `send_to_chatgpt` which sends the Python code to ChatGPT for generating the required documentation. It also defines the prompts used for generating the docstrings, README, and advisory.

## Getting Started

To get the project up and running on your local machine, follow the instructions below.

### Prerequisites

You will need the following to run this project:

- Python 3.7 or later
- `azure-identity` Python package
- `langchain` Python package

You can install these packages using pip:

```bash
pip install azure-identity langchain
```

### Installing

Clone the repository to your local machine:

```bash
git clone https://github.com/your-repo/python-code-documentation-generator.git
```

Navigate to the project directory:

```bash
cd python-code-documentation-generator
```

### Running the project

You can run the project using the following command:

```bash
python main.py --folder your_folder --dockstring --Readme --advisory
```

Replace `your_folder` with the path to the folder containing the Python files you want to process.

## Usage

Here is an example of how to use the project:

```bash
python main.py --folder ./my_python_files --dockstring --Readme
```

This command will process all Python files in the `my_python_files` directory and generate docstrings and a README file.

## Built Using

- Python
- OpenAI GPT-3
- Azure Identity
- Langchain

## Contributing

If you want to contribute to this project, please fork the repository, make your changes, and submit a pull request.

## Authors

- Your Name

## Acknowledgments

- OpenAI for providing the GPT-3 model
- Azure for their identity package
- Langchain for their chat models and output parsers