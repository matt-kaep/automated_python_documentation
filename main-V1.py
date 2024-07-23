import os
import ast
import requests
import astunparse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"


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

    prompt = ChatPromptTemplate.from_template("Please generate a documentation string for this function:{topic}")
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"topic": ast.unparse(function_def)})
    

    return completion.strip()

def add_docstring(function_def, docstring):
    function_def.body.insert(0, ast.parse(f"'''{docstring}'''").body[0])

def write_changes(file_path, tree):
    with open(file_path, "w") as file:
        file.write(astunparse.unparse(tree))

def main(root_dir):
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
