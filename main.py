import os
import time

import argparse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://elevengpt.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "4a8f724e3ef84157bc5378553d3dec14"

#os.environ["AZURE_OPENAI_ENDPOINT"] = "your_endpoint"
#os.environ["AZURE_OPENAI_API_KEY"] = "your_key"

def send_to_chatgpt(code, dockstrings_completion, Readme_completion, advisory_completion, model):
    """
    Summary: Sends the code to ChatGPT for generating docstrings, README, or advisory.
    Parameters:
        - code (str): The Python code to process.
        - dockstrings_completion (bool): Whether to generate docstrings.
        - Readme_completion (bool): Whether to generate a README file.
        - advisory_completion (bool): Whether to generate an advisory file.
        - model (str): The model to use for generating the output.
    Returns:
        str: The generated output.
    """
    llm = AzureChatOpenAI(
        #azure_deployment="gpt4_32k",
        azure_deployment=model,
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # organization="...",
        # other params...
    )
    if dockstrings_completion:
        prompt = ChatPromptTemplate.from_template(
        """Generate docstrings and comments for each function and each class in the provided Python code.
        The docstrings of the function should follow the NumPy docstring format and include the following sections:
        - Summary: A precise and comprehensive summary of what the function does.
        - Parameters: A list of each parameter, with a brief description of what it does.
        - Returns: A description of the return value(s) of the function.
        The dockstrings of the class should follow the classic docstring format for classes.
        Comments must be added at the end of the lines to explain the code inside or outside function and class.
        Do not add any introduction sentence or triple quotes to your answer, just the return of the prompt in only one block of code.
        ***
        Here is the code: {code}"""
        )
    if Readme_completion:
        prompt = ChatPromptTemplate.from_template(
            """Generate a README file for the provided project.
            The README file should follow the following pattern and include the following sections:

            Pattern:
            # Project Title
            One paragraph description of the project.

            ## About
            A brief description of what the project does and its purpose. An explanation of what each file in the project does.

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

    if advisory_completion:
        prompt = ChatPromptTemplate.from_template(
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

            6. References
            A list of links to relevant resources, such as bug reports or security advisories.

            Here is the code: {code}"""
        )

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"code": code})
    if completion[:9] == "```python":
        completion = completion[10:len(completion)-3]	
    return completion

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
                    docstrings = send_to_chatgpt(code, True, False, False, model = "eleven_gpt_35_turbo_16k")
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
            Readme_generation = send_to_chatgpt(Readme_promt_memory, False, True, False, model = "gpt4_32k")
            with open(dirpath + '/Generated_Readme.md', "w") as file:
                file.write(Readme_generation)
        if advisory_bool:
            advisory_generation = send_to_chatgpt(Readme_promt_memory, False, False, True, model = "gpt4_32k")
            with open(dirpath + '/Generated_advisory.md', "w") as file:
                file.write(advisory_generation)
    end_time = time.time()  # end timer
    elapsed_time = end_time - start_time  # calculate elapsed time
    print(f"{num_files_processed} files processed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add docstrings to Python code using ChatGPT.")
    parser.add_argument("folder", help="The root folder containing Python files to process.")
    parser.add_argument("--dockstring", help="Add dockstring to the functions in the python files.", action="store_true")
    parser.add_argument("--Readme", help="Generate a Readme file for the python files.", action="store_true")
    parser.add_argument("--advisory", help="Generate an advisory file for the python files.", action="store_true")
    args = parser.parse_args()
    main(args.folder, args.dockstring, args.Readme, args.advisory)
