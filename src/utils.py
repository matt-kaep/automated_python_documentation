import argparse
import ast
import os
import re
import subprocess
import textwrap

import astunparse
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


def get_function_definitions(file_path):
    """
    Summary:
    This function takes a file path as input and attempts to parse the file using the ast module. It then searches for all function definitions in the parsed tree and returns a list of these function definitions along with the parsed tree.

    Parameters:
    - file_path: A string representing the path to the file that needs to be parsed.

    Returns:
    A tuple containing two elements:
    1. function_defs: A list of ast.FunctionDef objects representing the function definitions found in the parsed tree.
    2. tree: The parsed tree generated from the file.
    If an error occurs during parsing, an empty list and None are returned.
    """
    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())
        function_defs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_defs.append(node)
        return (function_defs, tree)
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return ([], None)


def extract_key_elements(file_path):
    "\n    Summary: Extracts key elements from a Python file, including the file itself, functions, and classes along with their docstrings.\n\n    Parameters:\n    - file_path: A string representing the path to the Python file.\n\n    Returns:\n    - A string containing the extracted key elements, including the file, functions, and classes along with their docstrings.\n"
    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())
            code = file.read()
        elements = []
        file_name = os.path.basename(file_path)
        if file_name.find("main") != (-1):
            elements.append(f"File: {code}")
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements.append(
                    f"Function: {node.name} Docstring: {ast.get_docstring(node)} "
                )
            elif isinstance(node, ast.ClassDef):
                elements.append(
                    f"Class: {node.name} Docstring: {ast.get_docstring(node)} "
                )
        return "\n".join(elements)
    except Exception as e:
        print(f"Error extracting key elements from file {file_path}: {e}")
        return ""


def write_changes_function(file_path, tree, docstring_list, function_defs_list):
    "\n    Summary:\n    This function takes in a file path, an abstract syntax tree (AST), a list of docstrings, and a list of function definitions. It modifies the code in the file by inserting the corresponding docstrings for each function definition at the appropriate location.\n\n    Parameters:\n    - file_path (str): The path of the file to be modified.\n    - tree (ast.AST): The abstract syntax tree of the code in the file.\n    - docstring_list (list): A list of docstrings corresponding to each function definition.\n    - function_defs_list (list): A list of function definitions.\n\n    Returns:\n    None\n"
    try:
        code = astunparse.unparse(tree)
        for j, function_def in enumerate(function_defs_list):
            index = code.find(function_def.name)
            indentation = (" " * function_def.col_offset) + (4 * " ")
            docstring = textwrap.indent(docstring_list[j], indentation)
            pattern = re.compile("\\):\\s*")
            match = pattern.search(code[index:])
            insert_index = index + match.end()
            code = (
                (((code[:insert_index] + "\n") + docstring) + "\n") + indentation
            ) + code[insert_index:]
        with open(file_path, "w") as file:
            file.write(code)
    except Exception as e:
        print(f"Error writing changes to file {file_path}: {e}")


def send_to_chatgpt(
    code, dockstrings_completion, Readme_completion, advisory_completion, model
):
    "\n    Summary: Sends code to ChatGPT for completion and returns the completion.\n\n    Parameters:\n    - code (str): The code to be sent to ChatGPT for completion.\n    - dockstrings_completion (bool): If True, the code is treated as a docstring completion.\n    - Readme_completion (bool): If True, the code is treated as a Readme completion.\n    - advisory_completion (bool): If True, the code is treated as an advisory completion.\n    - model (str): The Azure deployment model to be used.\n\n    Returns:\n    - completion (str): The completion of the code sent to ChatGPT.\n"
    try:
        llm = AzureChatOpenAI(
            azure_deployment=model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        if dockstrings_completion:
            prompt = prompt_dockstring
            output_parser = StrOutputParser()
            chain = (prompt | llm) | output_parser
            completion = chain.invoke({"code": ast.unparse(code)})
            return completion.strip()
        if Readme_completion:
            prompt = prompt_Readme
        if advisory_completion:
            prompt = prompt_advisory
        output_parser = StrOutputParser()
        chain = (prompt | llm) | output_parser
        completion = chain.invoke({"code": code})
        if completion[:9] == "```python":
            completion = completion[10 : (len(completion) - 3)]
        return completion
    except Exception as e:
        print(f"Error sending code to ChatGPT: {e}")
        return ""


def reorganize_imports_in_directory(directory_path):
    "\n    Summary:\n    Reorganizes imports in all Python files within a given directory using the isort tool.\n\n    Parameters:\n    - directory_path: A string representing the path of the directory to be searched for Python files.\n\n    Returns:\n    None. Prints a message indicating that the imports have been reorganized.\n"
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    subprocess.run(["isort", file_path])
        print(
            f"Imports in {directory_path} have been reorganized according to best practices."
        )
    except Exception as e:
        print(f"Error reorganizing imports in directory {directory_path}: {e}")


prompt_dockstring = ChatPromptTemplate.from_template(
    "Generate docstrings for the function in the provided Python code.\n        The docstrings of the function should follow the NumPy docstring format and include the following sections:\n        - Summary: A precise and comprehensive summary of what the function does.\n        - Parameters: A list of each parameter, with a brief description of what it does.\n        - Returns: A description of the return value(s) of the function.\n        \n        Do not add any introduction sentence, just return the docstring without the rest of the function.\n        Add 3 double quotes at the beginning and end of the docstring.\n        Here is the code: {code}"
)
prompt_Readme = ChatPromptTemplate.from_template(
    "Generate a README file for the provided project.\n            The README file should follow the following pattern and include the following sections:\n            Pattern:\n            # Project Title\n            One paragraph description of the project.\n            ## About\n            A brief description of what the project does and its purpose. An explanation of what each file in the project does.\n            ## Directory Hierrachy\n            A list of the files in the project\n            ## Getting Started\n            Instructions on how to get the project up and running on a local machine.\n            ### Prerequisites\n            A list of things needed to install the software and how to install them.\n            ### Installing\n            Step-by-step instructions on how to install the project.\n            ### Running the project\n            Instructions on how to run the project.\n            ## Usage\n            Examples of how to use the project.\n            ## Built Using\n            A list of the technologies used to build the project.\n            ## Contributing\n            Instructions on how to contribute to the project.\n            ## Authors\n            A list of the authors of the project.\n            ## Acknowledgments\n            A list of any acknowledgments.\n            Here is the code: {code}"
)
prompt_advisory = ChatPromptTemplate.from_template(
    "Prompt:\n            Generate an advisory in markdown format for the provided project.\n            The advisory should include the following sections:\n\n            1. Code Summary\n            A comprehensive and complete summary of what the code does and its purpose.\n\n            2. Summary\n            A brief summary of the issues and their impact.\n\n            3. Issues\n            A list of the issues found in the code, including:\n            - A detailed description of the issue.\n            - The impact of the issue.\n            - An example of the affected code, if applicable.\n            - Recommendations for how to fix the issue.\n\n            4. Optimization Ideas\n            A list of ideas for optimizing the code, including:\n            - A detailed description of the optimization idea.\n            - The potential benefits of the optimization.\n            - An example of how to implement the optimization, if applicable.\n\n            5. Code Reorganization\n            Recommendations for how to reorganize the code to improve its structure and readability, including:\n            - A detailed description of the recommended changes.\n            - An example of how the code could be reorganized, if applicable.\n\n            6. Future Improvements\n            Suggestions for future improvements to the code, including:\n            - A detailed description of the improvements.\n            - The potential benefits of the improvements.\n            - An example of how to implement the improvements, if applicable.\n\n            7. References\n            A list of links to relevant resources, such as bug reports or security advisories.\n\n            Here is the code: {code}"
)
