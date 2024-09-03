# RAG Chatbot

This project is a chatbot that uses the RAG (Retrieval-Augmented Generation) model to answer questions based on the content of a PDF document. The chatbot ingests a PDF document, processes the text data, and uses it to generate responses to user queries.

## About

The project consists of two main Python files: `RAG.py` and `streamlit_UI_app.py`.

`RAG.py` contains the `ChatPDF` class, which is responsible for ingesting a PDF document, processing the text data, and generating responses to user queries. It uses the Azure Chat OpenAI API to generate responses.

`streamlit_UI_app.py` contains the user interface for the chatbot. It uses the Streamlit library to create a web-based interface where users can upload a PDF document and interact with the chatbot.

## Directory Hierarchy

- `RAG.py`
- `streamlit_UI_app.py`

## Getting Started

To get the project up and running on your local machine, follow these instructions.

### Prerequisites

You will need the following software installed on your machine:

- Python 3.6 or higher
- Streamlit
- Azure SDK for Python

You can install these using pip:

```
pip install streamlit azure
```

### Installing

To install the project, clone the repository to your local machine:

```
git clone https://github.com/yourusername/yourrepository.git
```

### Running the project

To run the project, navigate to the project directory and run the Streamlit app:

```
streamlit run streamlit_UI_app.py
```

## Usage

To use the chatbot, upload a PDF document using the file uploader in the Streamlit app. Then, enter your query in the text box and press enter. The chatbot will generate a response based on the content of the PDF document.

## Built Using

- Python
- Streamlit
- Azure Chat OpenAI API

## Contributing

To contribute to the project, please submit a pull request.

## Authors

- Your Name

## Acknowledgments

- Azure for their Chat OpenAI API
- Streamlit for their easy-to-use web app framework
- The creators of the RAG model for their innovative approach to question answering.