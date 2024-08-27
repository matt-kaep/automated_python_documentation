import argparse
import os
import ast
import textwrap
import requests
import astunparse
import autopep8
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import utils1 as utils
import time

#"python src/main1.py Test_code_on_this_folder --docstring"

def main(root_dir, docstring_bool = False, Readme_bool = False, advisory_bool = False):
    start_time = time.time()
    if not docstring_bool and not Readme_bool and not advisory_bool:
        print("No arguments provided. Please provide either 'dockstring' or 'Readme' or 'advisory' argument.")
        return
    if root_dir[:] =="":
        print("Please provide a valid root directory.")
        return
    
    Readme_promt_memory = ""

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if docstring_bool:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    function_defs, tree = utils.get_function_definitions(file_path)
                    function_defs_list = []
                    docstring_list = []
                    for function_def in function_defs:
                        docstring = utils.send_to_chatgpt(function_def, True, False, False, model = "eleven_gpt_35_turbo_16k")
                        docstring_list.append(docstring)
                        function_defs_list.append(function_def)
                    utils.write_changes_function(file_path, tree,docstring_list,function_defs_list)
            if Readme_bool or advisory_bool:
                Readme_promt_memory += f"## {filename}\n\n"
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, "r") as file:
                        code = file.read()
                    Readme_promt_memory += f"```python\n{code}\n```\n\n"
                Readme_promt_memory += "***\n\n"
        if Readme_bool:
            Readme_generation = utils.send_to_chatgpt(Readme_promt_memory, False, True, False, model = "gpt4_32k")
            with open(dirpath + '/Generated_Readme.md', "w") as file:
                file.write(Readme_generation)
        if advisory_bool:
            advisory_generation = utils.send_to_chatgpt(Readme_promt_memory, False, False, True, model = "gpt4_32k")
            with open(dirpath + '/Generated_advisory.md', "w") as file:
                file.write(advisory_generation)
    end_time = time.time()  # end timer
    elapsed_time = end_time - start_time  # calculate elapsed time
    print(f"Files processed in {elapsed_time} seconds.")


#Define command tools
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add docstrings to Python code using ChatGPT.")
    parser.add_argument("folder", help="The root folder containing Python files to process.")
    parser.add_argument("--docstring", help="Add docstring to the functions in the python files.", action="store_true")
    parser.add_argument("--Readme", help="Generate a Readme file for the python files.", action="store_true")
    parser.add_argument("--advisory", help="Generate an advisory file for the python files.", action="store_true")
    args = parser.parse_args()
    main(args.folder, args.docstring, args.Readme, args.advisory)

