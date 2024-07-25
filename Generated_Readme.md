# Python Code Documentation Generator

This project is a Python code documentation generator that uses OpenAI's GPT-3 model to generate docstrings, README files, and advisory files for Python code. It is designed to help developers automate the process of documenting their code, making it easier to understand and maintain.

## About

The project consists of two Python files: `main.py` and `utils.py`. 

`main.py` is the main script that processes Python files in a directory and generates docstrings, README, or advisory based on the arguments provided. It uses the `os` module to walk through the directory and the `argparse` module to handle command-line arguments.

`utils.py` contains the function `send_to_chatgpt` that sends the Python code to ChatGPT for generating the required documentation. It also defines the prompts for generating docstrings, README, and advisory.

## Getting Started

To get the project up and running on your local machine, follow the instructions below.

### Prerequisites

You need to have Python installed on your machine. You can download it from [here](https://www.python.org/downloads/). 

### Installing

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required packages using the command `pip install -r requirements.txt`.

### Running the project

To run the project, navigate to the project directory and run the command `python src/main.py --dockstring --Readme --advisory <folder>`.

## Usage

Here is an example of how to use the project:

`python src/main.py --dockstring --Readme --advisory Test_the_code_on_this_folder`

This command will process all Python files in the `Test_the_code_on_this_folder` directory and generate docstrings , a README file and an advisory file.

## Built Using

- Python
- OpenAI's GPT-3 model

## Contributing

If you want to contribute to this project, please fork the repository, make your changes, and create a pull request.

## Authors

- [Your Name]

## Acknowledgments

- OpenAI for providing the GPT-3 model.
- Python community for providing the necessary libraries and modules.