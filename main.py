import os
import time

import argparse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import utils as utils




def main(root_dir, dockstring_bool = False, Readme_bool = False, advisory_bool = False):
    """
    Summary: Main function to process Python files in a directory and generate docstrings, README, or advisory.
    Parameters:
        - root_dir (str): The root directory containing Python files to process.
        - dockstring_bool (bool): Whether to generate docstrings.
        - Readme_bool (bool): Whether to generate a README file.
        - advisory_bool (bool): Whether to generate an advisory file.
    """
    if not dockstring_bool and not Readme_bool and not advisory_bool:
        print("No arguments provided. Please provide either 'dockstring' or 'Readme' or 'advisory' argument.")
        return
    start_time = time.time()  # start timer
    num_files_processed = 0
    Readme_promt_memory = ""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if dockstring_bool:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, "r") as file:
                        code = file.read()
                    docstrings = utils.send_to_chatgpt(code, True, False, False, model = "eleven_gpt_35_turbo_16k")
                    with open(file_path[:len(file_path)-3] + '_commented.py', "w") as file:
                        file.write(docstrings)
                    num_files_processed += 1
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
    print(f"{num_files_processed} files processed in {elapsed_time:.2f} seconds.")


#Define command tools
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add docstrings to Python code using ChatGPT.")
    parser.add_argument("folder", help="The root folder containing Python files to process.")
    parser.add_argument("--dockstring", help="Add dockstring to the functions in the python files.", action="store_true")
    parser.add_argument("--Readme", help="Generate a Readme file for the python files.", action="store_true")
    parser.add_argument("--advisory", help="Generate an advisory file for the python files.", action="store_true")
    args = parser.parse_args()
    main(args.folder, args.dockstring, args.Readme, args.advisory)






