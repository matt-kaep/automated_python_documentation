import os
import time
import ast
import requests
import astunparse
import argparse
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain.chat_models import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://elevengpt.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "4a8f724e3ef84157bc5378553d3dec14"

def send_to_chatgpt(code):
    """
    Summary: Sends Python code to ChatGPT to generate docstrings and comments for each function.
    
    Parameters:
    - code (str): The Python code to process.
    
    Returns:
    - docstrings (str): The generated docstrings and comments for each function in the code.
    """
    llm = AzureChatOpenAI(
        azure_deployment="eleven_gpt_35_turbo_16k",
        api_version="2024-05-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_template(
        "Generate docstrings and comments for each function in the provided Python code. "
        "The docstrings should follow the NumPy docstring format and include the following sections: "
        "- Summary: A brief summary of what the function does. "
        "- Parameters: A list of each parameter, with a brief description of what it does. "
        "- Returns: A description of the return value(s) of the function. "
        "Comments should be added to explain any complex or non-obvious code. "
        "Do not add any introduction sentence or triple quotes to your answer, just the return of the prompt. "
        "Here is the code: {topic}"
    )

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    completion = chain.invoke({"topic": code})
    return completion

def main(root_dir):
    """
    Summary: Processes Python files in a root directory and adds docstrings to the functions using ChatGPT.
    
    Parameters:
    - root_dir (str): The root directory containing Python files to process.
    """
    start_time = time.time()  # start timer
    num_files_processed = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, "r") as file:
                    code = file.read()
                docstrings = send_to_chatgpt(code)
                with open(file_path[:len(file_path)-3] + '_commented.py', "w") as file:
                    file.write(docstrings)
                num_files_processed += 1
    end_time = time.time()  # end timer
    elapsed_time = end_time - start_time  # calculate elapsed time
    print(f"{num_files_processed} files processed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add docstrings to Python code using ChatGPT.")
    parser.add_argument("folder", help="The root folder containing Python files to process.")
    args = parser.parse_args()
    main(args.folder)