import argparse
import os
import ast
import textwrap
import requests
import astunparse
import re
import autopep8
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://elevengpt.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "4a8f724e3ef84157bc5378553d3dec14"

def get_function_definitions(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    function_defs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_defs.append(node)

    return function_defs, tree


def write_changes_function(file_path, tree,docstring_list,function_defs_list):
    code = astunparse.unparse(tree)
    for j, function_def in enumerate(function_defs_list):
        index = code.find(function_def.name)
        indentation = " " * (function_def.col_offset) + 4*" "
        docstring = textwrap.indent(docstring_list[j], indentation)
        pattern = re.compile(r'\):\s*')
        match = pattern.search(code[index:])

        insert_index = index + match.end()
        code = code[:insert_index] + "\n" + docstring + "\n" + indentation + code[insert_index:] 
    with open(file_path, "w") as file:
        file.write(code)



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
        prompt = prompt_dockstring
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        completion = chain.invoke({"code": ast.unparse(code)})
        return completion.strip()
    if Readme_completion:
        prompt = prompt_Readme
    if advisory_completion:
        prompt = prompt_advisory

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"code": code})
    if completion[:9] == "```python":
        completion = completion[10:len(completion)-3]	
    return completion


########################################################################
# DEFINE THE PROMPTS
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