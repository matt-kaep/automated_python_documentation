import argparse
import ast
import os
import subprocess
import sys
import textwrap
import time

import astunparse
import requests
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .utils import (
      extract_key_elements,
      get_function_definitions,
      reorganize_imports_in_directory,
      send_to_chatgpt,
      write_changes_function,
  )

#from utils import *

load_dotenv(dotenv_path='.env')


def main(root_dir, docstring_bool=False, Readme_bool=False, advisory_bool=False):
    """
    Summary:
    This function performs various tasks based on the provided arguments. It can generate docstrings for Python functions, create a README file, and generate an advisory file. It also reorganizes imports in the specified directory and formats the code using the 'black' tool.

    Parameters:
    - root_dir: A string representing the root directory where the function will perform its tasks.
    - docstring_bool: A boolean indicating whether to generate docstrings for Python functions. Default is False.
    - Readme_bool: A boolean indicating whether to create a README file. Default is False.
    - advisory_bool: A boolean indicating whether to generate an advisory file. Default is False.

    Returns:
    None
    """

    print("DOCSTRING_MODEL: ", os.getenv("MODEL_DOCSTRING"))

    start_time = time.time()
    if (not docstring_bool) and (not Readme_bool) and (not advisory_bool):
        print(
            "No arguments provided. Please provide either 'dockstring' or 'Readme' or 'advisory' argument."
        )
        return
    if root_dir[:] == "":
        print("Please provide a valid root directory.")
        return
    Readme_promt_memory = ""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if docstring_bool:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    (function_defs, tree) = get_function_definitions(file_path)
                    function_defs_list = []
                    docstring_list = []
                    for function_def in function_defs:
                        if not ast.get_docstring(function_def):
                            docstring = send_to_chatgpt(
                                function_def,
                                True,
                                False,
                                False,
                                model=os.getenv("MODEL_DOCSTRING"),
                            )
                            docstring_list.append(docstring)
                            function_defs_list.append(function_def)
                        else:
                            print(
                                f"Docstring already present for function: {function_def.name}"
                            )
                    write_changes_function(
                        file_path, tree, docstring_list, function_defs_list
                    )
            if Readme_bool or advisory_bool:
                Readme_promt_memory += f"## {filename}"
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    key_elements = extract_key_elements(file_path)
                    Readme_promt_memory += f"```python{key_elements}```"
                Readme_promt_memory += "***\n\n"
        if Readme_bool:
            Readme_generation = send_to_chatgpt(
                Readme_promt_memory, False, True, False, model=os.getenv("MODEL_README")
            )
            with open((dirpath + "/Generated_Readme.md"), "w") as file:
                file.write(Readme_generation)
        if advisory_bool:
            advisory_generation = send_to_chatgpt(
                Readme_promt_memory, False, False, True, model=os.getenv("MODEL_ADVISORY")
            )
            with open((dirpath + "/Generated_advisory.md"), "w") as file:
                file.write(advisory_generation)
    reorganize_imports_in_directory(root_dir)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Files processed in {elapsed_time} seconds.")
    # Run black formatting on all files in the root directory
    subprocess.run(["black", root_dir])


def run():

    parser = argparse.ArgumentParser(
        description="Add docstrings to Python code using ChatGPT."
    )
    parser.add_argument(
        "folder", help="The root folder containing Python files to process."
    )
    parser.add_argument(
        "--docstring",
        help="Add docstring to the functions in the python files.",
        action="store_true",
    )
    parser.add_argument(
        "--Readme",
        help="Generate a Readme file for the python files.",
        action="store_true",
    )
    parser.add_argument(
        "--advisory",
        help="Generate an advisory file for the python files.",
        action="store_true",
    )
    args = parser.parse_args()
    main(args.folder, args.docstring, args.Readme, args.advisory)


if __name__ == "__main__":
    run()
