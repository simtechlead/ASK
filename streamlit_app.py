import streamlit as st
import os
import time
from openai import OpenAI

# Include the CSS styles in your Streamlit app
st.markdown("""
<style>
/* Apply a background color to the whole page */
body {
    background-color: #ECE5DD; /* WhatsApp-like background color */
}

/* Style chat messages in Streamlit (You may need to inspect the actual Streamlit elements and adjust selectors accordingly) */
.css-1aumxhk {
    background-color: #DCF8C6; /* Light green background for messages */
    border-radius: 18px; /* Rounded corners for chat bubbles */
}

/* Style for the chat message input box */
.css-1cpxqw2 {
    border-radius: 18px; /* Rounded corners for the input box */
}

/* Style for the send button */
button {
    border-radius: 50%; /* Rounded corners for buttons, resembling WhatsApp's send button */
    background-color: #25D366; /* WhatsApp-like green color */
}
</style>
""", unsafe_allow_html=True)

# Set up the page configuration and title
st.set_page_config(page_title="ASK")
st.title('Asisten Kuria GKPS Cikoko')

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
    with st.container():
        st.write(message["content"], unsafe_allow_html=True)

# React to user input
user_input = st.text_input("Hal apa yang ingin ditanyakan?", key="input")
if st.button("Send"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get responses from OpenAI
    responses = interact_with_openai(user_input)
    for response in responses:
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear the input box after sending the message
    st.session_state.input = ""
