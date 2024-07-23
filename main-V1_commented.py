import os
import ast
import requests
import astunparse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://elevengpt.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "4a8f724e3ef84157bc5378553d3dec14"

def get_function_definitions(file_path):
    """
    Summary: Retrieves all function definitions from a Python file.

    Parameters:
    - file_path (str): The path to the Python file.

    Returns: 
    - function_defs (list): A list of ast.FunctionDef objects representing the function definitions in the file.
    - tree (ast.Module): The abstract syntax tree of the Python file.
    """
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    function_defs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_defs.append(node)

    return function_defs, tree

def send_to_chatgpt(function_def):
    """
    Summary: Sends a function definition to ChatGPT to generate a documentation string.

    Parameters:
    - function_def (ast.FunctionDef): The function definition to be documented.

    Returns: 
    - completion (str): The generated documentation string.
    """
    llm = AzureChatOpenAI(
        azure_deployment="gpt4_32k",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # organization="...",
        # other params...
    )

    prompt = ChatPromptTemplate.from_template("Please generate a documentation string for this function:{topic}")
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"topic": ast.unparse(function_def)})

    return completion.strip()

def add_docstring(function_def, docstring):
    """
    Summary: Adds a docstring to a function definition.

    Parameters:
    - function_def (ast.FunctionDef): The function definition to add the docstring to.
    - docstring (str): The docstring to be added.
    """
    function_def.body.insert(0, ast.parse(f"'''{docstring}'''").body[0])

def write_changes(file_path, tree):
    """
    Summary: Writes the modified abstract syntax tree back to the Python file.

    Parameters:
    - file_path (str): The path to the Python file.
    - tree (ast.Module): The modified abstract syntax tree.
    """
    with open(file_path, "w") as file:
        file.write(astunparse.unparse(tree))

def main(root_dir):
    """
    Summary: Generates docstrings for all function definitions in Python files within a directory.

    Parameters:
    - root_dir (str): The root directory to search for Python files.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                function_defs, tree = get_function_definitions(file_path)
                for function_def in function_defs:
                    docstring = send_to_chatgpt(function_def)
                    add_docstring(function_def, docstring)
                    print(f"Generated docstring for function: {ast.unparse(function_def)}")
                    print(docstring)
                write_changes(file_path, tree)

if __name__ == "__main__":
    main("C:/Users/MatthieuKAEPPELIN/Documents/automated_python_commentary/test_folder")