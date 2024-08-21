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
        azure_deployment="gpt4_32k",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # organization="...",
        # other params...
    )

    prompt = ChatPromptTemplate.from_template("Please generate a documentation string for this function:{topic}. You should use the usual docstring format.")
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"topic": ast.unparse(function_def)})
    return completion.strip()




def write_changes(file_path, tree,docstring):
    i=0
    docstring = textwrap.indent(docstring, "    ")
    code = astunparse.unparse(tree)
    while code[i]!=":":
        i+=1
    code = code[:i+1] + " \n" + docstring + "\n" + code[i+1:]
    with open(file_path, "w") as file:
        file.write(code)


def main(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                function_defs, tree = get_function_definitions(file_path)
                for function_def in function_defs:
                    docstring = send_to_chatgpt(function_def)
                write_changes(file_path, tree,docstring)

#Define command tools
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add docstrings to Python code using ChatGPT.")
    parser.add_argument("folder", help="The root folder containing Python files to process.")
    parser.add_argument("--dockstring", help="Add dockstring to the functions in the python files.", action="store_true")
    parser.add_argument("--Readme", help="Generate a Readme file for the python files.", action="store_true")
    parser.add_argument("--advisory", help="Generate an advisory file for the python files.", action="store_true")
    args = parser.parse_args()
    main(args.folder, args.dockstring, args.Readme, args.advisory)
