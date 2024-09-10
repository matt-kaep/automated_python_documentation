import os
import tempfile

import streamlit as st
from rag import ChatPDF
from streamlit_chat import message

st.set_page_config(page_title="ChatPDF")


def display_messages():
    """
    Summary:
    This function is used to display a chat interface for uploading a PDF document, sending messages, and processing user input.

    Parameters:
    - No parameters.

    Returns:
    - No return value.
    """

    """
    Summary:
    Displays chat messages in a chat interface.

    Parameters:
    - None

    Returns:
    - None
    """
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    """
    Summary:
    This function processes the user input by stripping any leading or trailing whitespace and then using the 'assistant' object to generate a response. The user input and the generated response are then appended to the 'messages' list in the 'st.session_state' dictionary.

    Parameters:
    None

    Returns:
    None
    """

    if (
        st.session_state["user_input"]
        and len(st.session_state["user_input"].strip()) > 0
    ):
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))


def read_and_save_file():
    """
    Summary:
    This function reads and saves a file. It clears the session state of the 'assistant' variable, initializes an empty list for 'messages', and sets 'user_input' to an empty string. It then iterates over each file in the 'file_uploader' session state. For each file, it creates a temporary file and writes the contents of the file to it. It retrieves the file path and uses it to ingest the file into the 'assistant' session state. Finally, it removes the temporary file.

    Parameters:
    None

    Returns:
    None
    """

    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(
            f"Ingesting {file.name}"
        ):
            st.session_state["assistant"].ingest(file_path)
        os.remove(file_path)


def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()

    st.header("ChatPDF")

    st.subheader("Upload a document")
    st.file_uploader(
        "Upload document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)


if __name__ == "__main__":
    page()
