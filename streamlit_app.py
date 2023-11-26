import streamlit as st
import os
import time
from openai import OpenAI
import datetime
import pytz
import dateparser  # For advanced date interpretation
import re  # For regular expressions

# Function to get the current time in Jakarta timezone
def get_current_time():
    jakarta_timezone = pytz.timezone("Asia/Jakarta")
    jakarta_time = datetime.datetime.now(jakarta_timezone)
    return jakarta_time.strftime("%H:%M:%S")

# Function to interpret date phrases using dateparser
def interpret_date_phrase(phrase):
    # Use dateparser to interpret the phrase
    current_date = datetime.datetime.now()
    if phrase in ["this morning", "pagi ini"]:
        return current_date.replace(hour=9, minute=0, second=0, microsecond=0)
    elif phrase in ["this noon", "siang ini"]:
        return current_date.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        interpreted_date = dateparser.parse(phrase, settings={'PREFER_DATES_FROM': 'future'})
        return interpreted_date

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    try:
        time_related_responses = {
            "what time is it": get_current_time(),
            "jam berapa sekarang": get_current_time()
        }

        # Check if the user message is a time-related query
        for query, response in time_related_responses.items():
            if query in user_message.lower():
                return [response]

        # Extract potential date-related phrases using regex
        date_phrases = re.findall(r"\b(besok|kemarin|minggu ini|minggu depan|hari ini|pagi ini|siang ini)\b", user_message, re.IGNORECASE)
        date_info = ""
        if date_phrases:
            # Interpret the first date phrase found
            relevant_date = interpret_date_phrase(date_phrases[0])
            if relevant_date:
                date_info = f" (Interpreted date: {relevant_date.strftime('%Y-%m-%d %H:%M:%S')})"

        # Include the date information in the query to OpenAI
        user_message = "Respond in Indonesian: " + user_message + date_info
        
        openai_key = os.environ['OPENAI_KEY']
        org_ID = os.environ['ORG_ID']

        client = OpenAI(organization=org_ID, api_key=openai_key)
        assistant = client.beta.assistants.retrieve("asst_kehD6QVaQfE8FFSf3Yfyaj0l")
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == 'completed':
                break
            else:
                time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        responses = []
        for each in messages:
            if each.role == 'assistant':
                responses.append(each.content[0].text.value if isinstance(each.content, list) and hasattr(each.content[0], 'text') else str(each.content))
        return responses

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Set up the page configuration and title
st.set_page_config(page_title="ASK")
st.title('Asisten Kuria GKPS Cikoko')

# Add user guide
st.info("Masukkan pertanyaan di kolom chat")

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
