import streamlit as st
import os
import time
from openai import OpenAI
import datetime
import pytz
import locale

# Set up the page configuration and title
st.set_page_config(page_title="ASK")
st.title('Simulasi Asisten Kuria GKPS Cikoko')

# Set the locale to Indonesian
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

# Display the current date and day in Indonesian timezone
tz = pytz.timezone('Asia/Jakarta')  # Set the timezone to Jakarta
current_time = datetime.datetime.now(tz)  # Get the current date and time in the specified timezone
current_date = current_time.strftime("%Y-%m-%d")
current_day = current_time.strftime("%A")  # Get the current day of the week in Indonesian

st.write(f"Tanggal saat ini: {current_date}, Hari: {current_day}")  # Display the current date and day

# Add user guide
st.info("""Masukkan pertanyaan di kolom chat""")

# Function to interact with OpenAI API
def interact_with_openai(user_message):
    try:
        # Prepend a directive to respond in Indonesian
        user_message = "Respond in Indonesian: " + user_message
        
        openai_key = os.environ['OPENAI_KEY']
        org_ID = os.environ['ORG_ID']

        client = OpenAI(organization=org_ID, api_key=openai_key)
        assistant = client.beta.assistants.retrieve("asst_zAV8KhNBHBtBtnUGwMfKW1YS")
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
