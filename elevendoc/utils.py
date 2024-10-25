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
from langchain_community.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(dotenv_path=".env")

import ast

import isort


def get_function_definitions(file_path):
    """
    Summary:
    This function parses the file using the ast module and searches for function definitions,
    including those within classes. It handles both sync and async functions.

    Parameters:
    - file_path: A string representing the path to the file.

    Returns:
    A tuple containing two elements:
    1. function_defs: A list of tuples, each containing the name of the class (or None if not inside a class) and an ast.FunctionDef or ast.AsyncFunctionDef object representing the function.
    2. tree: The parsed tree generated from the file.
    """

    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())

        function_defs = []
        class_stack = []  # Stack to track current class nesting

        # Define a recursive helper to process nodes
        def visit_node(node, current_class=None):
            # Track if we're in a class scope
            if isinstance(node, ast.ClassDef):
                class_stack.append(node.name)  # Enter the class
                for item in node.body:
                    visit_node(item, class_stack[-1])
                class_stack.pop()  # Exit the class
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_defs.append((current_class, node))

        # Traverse the AST tree
        for node in tree.body:
            visit_node(node)

        return (function_defs, tree)

    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return ([], None)


def extract_key_elements(file_path):
    """
    Summary: Extracts key elements from a Python file, including file name, functions,
    (both sync and async) and classes.

    Parameters:
    - file_path: A string representing the path to the Python file.

    Returns:
    - A string containing the extracted key elements, separated by newlines.
    """

    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())
            code = file.read()
        elements = []
        file_name = os.path.basename(file_path)
        if file_name.find("main") != (-1):
            elements.append(f"File: {code}")
        for node in ast.walk(tree):
            # Handle both regular and async functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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


import re
import textwrap


def write_changes_function(
    file_path, tree, docstring_list, function_defs_list, force_bool, verbose=False
):
    """
    Summary: Writes docstrings to specified functions in a Python file. Handles functions within classes.

    Parameters:
        - file_path (str): The path to the Python file.
        - tree (ast.Module): The abstract syntax tree of the Python file.
        - docstring_list (list): A list of docstrings to be added to the functions.
        - function_defs_list (list): A list of tuples containing class name (or None) and function definitions.
        - force_bool (bool): A boolean value indicating whether to overwrite existing docstrings.

    Returns: None
    """

    try:
        with open(file_path, "r") as file:
            code = file.read()
        for j, (class_name, function_def) in enumerate(function_defs_list):
            if verbose:
                print(f"Processing function {function_def.name} in class {class_name}")

            if class_name:
                # Use regex to match the class definition more robustly
                class_pattern = re.compile(
                    rf"class\s+{class_name}\s*(\([\w\s,]*\))?\s*:", re.MULTILINE
                )
                class_match = class_pattern.search(code)

                if not class_match:
                    raise ValueError(f"Class {class_name} not found in the file.")

                # Find the function definition within the class context
                function_index = code.find(
                    f"def {function_def.name}", class_match.start()
                )
            else:
                # If no class (function outside class), search globally
                function_index = code.find(f"def {function_def.name}")

            if function_index == -1:
                raise ValueError(f"Function {function_def.name} not found in the file.")

            # Construct the docstring and indentation
            indentation = (" " * function_def.col_offset) + (4 * " ")
            docstring = textwrap.indent(docstring_list[j], indentation)

            # Find the location to insert the docstring (after the function signature)
            pattern = re.compile(
                r"\)\s*(->\s*[\w\[\], |]+)?\s*:"
            )  # end of function signature
            match = pattern.search(code[function_index:])
            insert_index = function_index + match.end()

            if force_bool:
                # Find and delete any existing docstring after insert_index
                existing_docstring_pattern = re.compile(r'""".*?"""', re.DOTALL)
                existing_docstring_match = existing_docstring_pattern.search(
                    code[insert_index:]
                )
                if existing_docstring_match:
                    start, end = existing_docstring_match.span()
                    code = code[: insert_index + start] + code[insert_index + end :]

            # Insert the new docstring
            code = (
                (((code[:insert_index] + "\n") + docstring) + "\n") + indentation
            ) + code[insert_index:]

        # Write the updated code back to the file
        with open(file_path, "w") as file:
            file.write(code)

    except Exception as e:
        print(f"Error writing changes to file {file_path}: {e}")


def send_to_chatgpt(
    code,
    Readme_dictionary,
    description,
    dockstrings_completion,
    Readme_completion,
    advisory_completion,
    model,
):
    """
    Summary:
        Sends code and a project description to ChatGPT for completion and returns the completed code
        or documentation based on the specified task type.

    Description:
        This function interacts with the AzureChatOpenAI model to complete parts of the provided code or
        documentation. The project description is passed to the model along with the code, allowing the model
        to generate more accurate and context-aware responses.

    Parameters:
        - code: The code to be sent to ChatGPT for completion.
        - description: A description of the project to be included for better context in the completion.
        - dockstrings_completion: A boolean indicating whether to perform docstring completion.
        - Readme_completion: A boolean indicating whether to perform README completion.
        - advisory_completion: A boolean indicating whether to perform advisory completion.
        - model: The Azure deployment model to be used for completion.

    Returns:
        The completed code or documentation as a string, depending on the selected completion type.

    Raises:
        - Exception: If an error occurs during communication with ChatGPT.
    """

    try:
        llm = AzureChatOpenAI(
            azure_deployment=model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        output_parser = StrOutputParser()

        # Decide the prompt based on the type of completion
        if dockstrings_completion:
            prompt = prompt_dockstring
            chain = (prompt | llm) | output_parser
            completion = chain.invoke(
                {"code": ast.unparse(code), "description": description}
            )
        elif Readme_completion:
            author = Readme_dictionary["author"]
            project_name = Readme_dictionary["project_name"]
            prompt = prompt_Readme
            chain = (prompt | llm) | output_parser
            completion = chain.invoke(
                {
                    "code": code,
                    "description": description,
                    "author": author,
                    "project_name": project_name,
                }
            )
        elif advisory_completion:
            prompt = prompt_advisory
            chain = (prompt | llm) | output_parser
            completion = chain.invoke({"code": code, "description": description})
        else:
            raise ValueError("No valid completion type specified.")

        print("debug1 step ok")

        # Post-process the completion (strip code block markers if present)
        if completion[:9] == "```python":
            completion = completion[10 : (len(completion) - 3)]

        return completion.strip()

    except Exception as e:
        print(f"Error sending code to ChatGPT: {e}")
        return ""


def reorganize_imports_in_directory(directory_path):
    """
    Summary:
    This function reorganizes the imports in all Python files within a given directory according to best practices.

    Parameters:
    - directory_path: A string representing the path of the directory to be processed. It should be a valid directory path.

    Returns:
    This function does not return any value.
    """
    directory_path = os.path.abspath(directory_path)
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    subprocess.run(["isort", file_path])
    except Exception as e:
        print(f"Error reorganizing imports in directory {directory_path}: {e}")


prompt_dockstring = ChatPromptTemplate.from_template(
    """
    ---Role---
    You're a helpful assistant designed to generate docstrings for Python functions.

    ---Goal---
    Generate docstrings for the function in the provided Python project.

    ---description---
    {description}

    ---Format---
    The docstrings of the function should follow the NumPy docstring format and include the following sections:
    - Summary: A precise and comprehensive summary of what the function does.
    - Parameters: A list of each parameter, with a brief description of what it does.
    - Returns: A description of the return value(s) of the function.
    
    Do not add any introduction sentence, just return the docstring without the rest of the function.
    Do not return in a code block, just return a string.
    Add 3 double quotes at the beginning and end of the docstring.

    ---Code---
    {code}
    
    ---Output---
    
    """
)

prompt_Readme = ChatPromptTemplate.from_template(
    """
    ---Role---
    You're a helpful assistant designed to generate comprehensive README files for Python data science projects.

    ---Goal---
    Your goal is to create a detailed README file for the provided project that effectively communicates its purpose and usage.

    ---Project Description---
    {description}

    ---Format---
    The README file should adhere to the following structure and include these essential sections:

        # Project Title
        The title is {project_name}. If it is empty, find a title that best describes the project.

        ## Overview
        A brief description of what the project does, its objectives, and its significance in the context of data science.

        ## About
        A more detailed explanation of the project, covering:
        - What the project does and its primary features.
        - An overview of each file in the project, including its role and functionality.

        ## Directory Hierarchy
        A clear list of the project's files and their organization within the directory.

        ## Getting Started
        Step-by-step instructions to help users set up the project locally.

        ### Prerequisites
        A list of necessary tools and libraries to install before running the project, along with instructions for installation.

        ### Installation
        Clear, sequential instructions for installing the project, ensuring ease of use.

        ### Running the Project
        Detailed instructions on how to execute the project, including any commands that need to be run.

        ## Usage
        Practical examples demonstrating how to utilize the project effectively, including code snippets.

        ## Technologies Used
        A comprehensive list of the technologies and frameworks that were used to build the project.

        ## Contributing
        Guidelines for contributing to the project, encouraging collaboration and community involvement.

        ## Authors
        Acknowledgment of the project's authors and contributors.
        Here is the author: {author}

        ## Acknowledgments
        Recognition of any resources or individuals who supported the development of the project.

    ---Code---
    {code}

    ---Instructions---
    Use the provided project description and code to generate a coherent and informative README file that addresses the specified sections and follows the outlined structure.

    ---Output---
    """
)


prompt_advisory = ChatPromptTemplate.from_template(
    """
---Role---
You're a helpful assistant designed to generate advisory reports for code projects.

---Goal---
Your goal is to generate an advisory in markdown format for the provided project.

---Description---
{description}

---Format---
The advisory should follow the pattern and include the following sections:

1. **Code Summary**  
   A comprehensive and complete summary of what the code does and its purpose.

2. **Summary**  
   A brief summary of the issues and their impact.

3. **Issues**  
   A list of the issues found in the code, including:
   - A detailed description of the issue.
   - The impact of the issue.
   - An example of the affected code, if applicable.
   - Recommendations for how to fix the issue.

4. **Optimization Ideas**  
   A list of ideas for optimizing the code, including:
   - A detailed description of the optimization idea.
   - The potential benefits of the optimization.
   - An example of how to implement the optimization, if applicable.

5. **Code Reorganization and Formatting**  
   Recommendations for how to reorganize the code to improve its structure and readability, including:
   - A detailed description of the recommended changes.
   - An example of how the code could be reorganized, if applicable.
   - A list of the unclear variable and function names, with proposed new names for each of them.

6. **Future Improvements**  
   Suggestions for future improvements to the code, including:
   - A detailed description of the improvements.
   - The potential benefits of the improvements.
   - An example of how to implement the improvements, if applicable.

7. **References**  
   A list of links to relevant resources, such as bug reports or security advisories.

---Code---
{code}

---Output---
"""
)
