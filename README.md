
<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="readme_logo.png" alt="Project logo"></a>
</p>

<h3 align="center">Automated Python Commentary</h3>

<div align="center">



</div>

---

<p align="center"> This project uses the Azure OpenAI service to automatically generate docstrings and comments for Python code.
    <br>
</p>


## 🧐 About <a name = "about"></a>

This project uses the Azure OpenAI service to automatically generate docstrings and comments for Python code. It walks through a directory tree, finds all Python files, reads the code from each file, sends the code to the OpenAI service to generate docstrings and comments, and writes the modified code back to a new file with the suffix '_commented.py'.

## 🏁 Getting Started <a name = "getting_started"></a>

To get started with this project, you will need to have Python 3.x installed on your machine. You will also need to set up an Azure OpenAI resource and obtain an API key. Once you have these prerequisites, you can run the project from the command line by specifying the root folder containing the Python files you want to process.

Use the last version main-V3.py for getting the dockstrings and the commentary.

### Prerequisites

- Python 3.x
- Azure OpenAI resource
- Azure OpenAI API key

### Installing

1. Clone the repository to your local machine.
2. Install the required packages using pip:

```shell
pip install azure-identity langchain openai astunparse
```

3. Set the environment variables for the Azure OpenAI API key and endpoint:
```bash
export OPENAI_API_KEY=<your_api_key>
export AZURE_OPENAI_ENDPOINT=<your_endpoint>
```

### Running the project
To run the project, open a command prompt or terminal window and navigate to the root folder of the project. Then run the following command:
```shell
python main-V3.py <path_to_root_folder>
```
Replace <path_to_root_folder> with the path to the root folder containing the Python files you want to process.
