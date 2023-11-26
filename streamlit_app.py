import streamlit as st
import os
import time
from openai import OpenAI
import datetime
import re  # For regular expressions

# Set up the page configuration and title
st.set_page_config(page_title="ASK")
st.title('Asisten Kuria GKPS Cikoko')

# Add user guide
st.info("Masukkan pertanyaan di kolom chat")

# Function to interpret date phrases
def interpret_date_phrase(phrase):
    current_date = datetime.datetime.now()
    if phrase == "besok":
        return current_date + datetime.timedelta(days=1)
    elif phrase == "kemarin":
        return current_date - datetime.timedelta(days=1)
    elif phrase == "minggu depan":
        return current_date + datetime.timedelta(weeks=1)
    # Add more interpretations as needed
    return current_date  # Default to current date if no match

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    try:
        # Extract date-related phrases from user_message using regex or string analysis
        date_phrases = re.findall(r"besok|kemarin|minggu depan", user_message)
        if date_phrases:
            # Interpret the first date phrase found
            relevant_date = interpret_date_phrase(date_phrases[0])
            # Modify user_message or fetch document based on relevant_date
            # For example, append the date to the message
            user_message += f" (Tanggal yang dimaksud: {relevant_date.strftime('%Y-%m-%d')})"

        # Prepend a directive to respond in Indonesian
        user_message = "Respond in Indonesian: " + user_message
        
        # [Rest of your existing code for interacting with OpenAI API]

        return responses

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Hal apa yang ingin ditanyakan?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get responses from OpenAI
    responses = interact_with_openai(user_input)
    for response in responses:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
