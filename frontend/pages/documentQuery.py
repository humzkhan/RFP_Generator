import streamlit as st
import requests
import sys
import os


st.markdown( "# Document Query")

st.sidebar.markdown("## WELCOME TO DOCUMENT QUERY")

# Flask server URL
ASK_URL = 'http://127.0.0.1:5500/ask'

def ask_question(question):
    if not question:
        st.error("Question is required")
        return

    payload = {"question": question}
    try:
        response = requests.post(ASK_URL, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            st.success("Answer: " + response_data["response"])
        else:
            st.error(response_data["error"])
    except Exception as e:
        st.error(str(e))


# Ask question section
st.header("Ask a Question")
question = st.text_input("Question")
if st.button("Send Question"):
    ask_question(question)