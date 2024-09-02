
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

os.environ['OPENAI_API_VERSION'] = '2024-05-01-preview'
load_dotenv()

def get_function_definitions(file_path):
    
    """
    Summary:
    This function takes a file path as input and returns a list of function definitions found in the file, along with the abstract syntax tree (AST) of the file.

    Parameters:
    - file_path: A string representing the path of the file to be parsed. It should include the file name and extension.

    Returns:
    A tuple containing two elements:
    1. function_defs: A list of ast.FunctionDef objects representing the function definitions found in the file.
    2. tree: The abstract syntax tree (AST) of the file, generated using the ast.parse() function.
    """
    try:
        with open(file_path, 'r') as file:
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
    
    """
    Summary: Extracts key elements from a Python file, including the file itself, functions, and classes along with their docstrings.

    Parameters:
    - file_path: A string representing the path to the Python file.

    Returns: 
    - A string containing the extracted key elements, including the file, functions, and classes along with their docstrings.
    """
    try:
        with open(file_path, 'r') as file:
            tree = ast.parse(file.read())
            code = file.read()
        elements = []
        file_name = os.path.basename(file_path)
        if (file_name.find('main') != (- 1)):
            elements.append(f'File: {code}')
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                elements.append(f'Function: {node.name} Docstring: {ast.get_docstring(node)} ')
            elif isinstance(node, ast.ClassDef):
                elements.append(f'Class: {node.name} Docstring: {ast.get_docstring(node)} ')
        return '\n'.join(elements)
    except Exception as e:
        print(f"Error extracting key elements from file {file_path}: {e}")
        return ''

def write_changes_function(file_path, tree, docstring_list, function_defs_list):
    
    """
    Summary: 
    This function takes in a file path, an abstract syntax tree (AST), a list of docstrings, and a list of function definitions. It modifies the code in the file by inserting the corresponding docstrings for each function definition at the appropriate location.

    Parameters:
    - file_path (str): The path of the file to be modified.
    - tree (ast.AST): The abstract syntax tree of the code in the file.
    - docstring_list (list): A list of docstrings corresponding to each function definition.
    - function_defs_list (list): A list of function definitions.

    Returns:
    None
    """
    try:
        code = astunparse.unparse(tree)
        for (j, function_def) in enumerate(function_defs_list):
            index = code.find(function_def.name)
            indentation = ((' ' * function_def.col_offset) + (4 * ' '))
            docstring = textwrap.indent(docstring_list[j], indentation)
            pattern = re.compile('\\):\\s*')
            match = pattern.search(code[index:])
            insert_index = (index + match.end())
            code = (((((code[:insert_index] + '\n') + docstring) + '\n') + indentation) + code[insert_index:])
        
        with open(file_path, 'w') as file:
            file.write(code)
    except Exception as e:
        print(f"Error writing changes to file {file_path}: {e}")


def send_to_chatgpt(code, dockstrings_completion, Readme_completion, advisory_completion, model):
    
    """
    Summary: Sends code to ChatGPT for completion and returns the completion.

    Parameters:
    - code (str): The code to be sent to ChatGPT for completion.
    - dockstrings_completion (bool): If True, the code is treated as a docstring completion.
    - Readme_completion (bool): If True, the code is treated as a Readme completion.
    - advisory_completion (bool): If True, the code is treated as an advisory completion.
    - model (str): The Azure deployment model to be used.

    Returns:
    - completion (str): The completion of the code sent to ChatGPT.
    """
    try:
        llm = AzureChatOpenAI(azure_deployment=model, api_version='2024-05-01-preview', temperature=0, max_tokens=None, timeout=None, max_retries=2)
        if dockstrings_completion:
            prompt = prompt_dockstring
            output_parser = StrOutputParser()
            chain = ((prompt | llm) | output_parser)
            completion = chain.invoke({'code': ast.unparse(code)})
            return completion.strip()
        if Readme_completion:
            prompt = prompt_Readme
        if advisory_completion:
            prompt = prompt_advisory
        output_parser = StrOutputParser()
        chain = ((prompt | llm) | output_parser)
        completion = chain.invoke({'code': code})
        if (completion[:9] == '```python'):
            completion = completion[10:(len(completion) - 3)]
        return completion
    except Exception as e:
        print(f"Error sending code to ChatGPT: {e}")
        return ''

def reorganize_imports_in_directory(directory_path):
    
    """
    Summary:
    Reorganizes imports in all Python files within a given directory using the isort tool.

    Parameters:
    - directory_path: A string representing the path of the directory to be searched for Python files.

    Returns:
    None. Prints a message indicating that the imports have been reorganized.
    """
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    subprocess.run(['isort', file_path])
        print(f'Imports in {directory_path} have been reorganized according to best practices.')
    except Exception as e:
        print(f"Error reorganizing imports in directory {directory_path}: {e}")




prompt_dockstring = ChatPromptTemplate.from_template(
        """Generate docstrings for the function in the provided Python code.
        The docstrings of the function should follow the NumPy docstring format and include the following sections:
        - Summary: A precise and comprehensive summary of what the function does.
        - Parameters: A list of each parameter, with a brief description of what it does.
        - Returns: A description of the return value(s) of the function.
        
        Do not add any introduction sentence, just return the docstring without the rest of the function.
        Add 3 double quotes at the beginning and end of the docstring.
        Here is the code: {code}"""
        )

prompt_Readme = ChatPromptTemplate.from_template(
            """Generate a README file for the provided project.
            The README file should follow the following pattern and include the following sections:
            Pattern:
            # Project Title
            One paragraph description of the project.
            ## About
            A brief description of what the project does and its purpose. An explanation of what each file in the project does.
            ## Directory Hierrachy
            A list of the files in the project
            ## Getting Started
            Instructions on how to get the project up and running on a local machine.
            ### Prerequisites
            A list of things needed to install the software and how to install them.
            ### Installing
            Step-by-step instructions on how to install the project.
            ### Running the project
            Instructions on how to run the project.
            ## Usage
            Examples of how to use the project.
            ## Built Using
            A list of the technologies used to build the project.
            ## Contributing
            Instructions on how to contribute to the project.
            ## Authors
            A list of the authors of the project.
            ## Acknowledgments
            A list of any acknowledgments.
            Here is the code: {code}"""
        )

prompt_advisory = ChatPromptTemplate.from_template(
            """Prompt:
            Generate an advisory in markdown format for the provided project.
            The advisory should include the following sections:

            1. Code Summary
            A comprehensive and complete summary of what the code does and its purpose.

            2. Summary
            A brief summary of the issues and their impact.

            3. Issues
            A list of the issues found in the code, including:
            - A detailed description of the issue.
            - The impact of the issue.
            - An example of the affected code, if applicable.
            - Recommendations for how to fix the issue.

            4. Optimization Ideas
            A list of ideas for optimizing the code, including:
            - A detailed description of the optimization idea.
            - The potential benefits of the optimization.
            - An example of how to implement the optimization, if applicable.

            5. Code Reorganization
            Recommendations for how to reorganize the code to improve its structure and readability, including:
            - A detailed description of the recommended changes.
            - An example of how the code could be reorganized, if applicable.

            6. Future Improvements
            Suggestions for future improvements to the code, including:
            - A detailed description of the improvements.
            - The potential benefits of the improvements.
            - An example of how to implement the improvements, if applicable.

            7. References
            A list of links to relevant resources, such as bug reports or security advisories.

            Here is the code: {code}"""
        )