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

def send_to_chatgpt(function_def):
    llm = AzureChatOpenAI(
        azure_deployment="eleven_gpt_35_turbo_16k",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # organization="...",
        # other params...
    )

    prompt = ChatPromptTemplate.from_template(
        """Generate docstrings for the function in the provided Python code.
        The docstrings of the function should follow the NumPy docstring format and include the following sections:
        - Summary: A precise and comprehensive summary of what the function does.
        - Parameters: A list of each parameter, with a brief description of what it does.
        - Returns: A description of the return value(s) of the function.
        
        Do not add any introduction sentence, just return the docstring without the rest of the function.
        Add 3 double quotes at the beginning and end of the docstring.
        Here is the code: {topic}"""
        )
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"topic": ast.unparse(function_def)})
    return completion.strip()




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