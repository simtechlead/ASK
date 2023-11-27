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

# Add this to the top of your script to include custom styles
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")  # Assuming you have a CSS file named 'style.css'

/* Add this content to your style.css file */

/* Apply WhatsApp color scheme */
body {
    background-color: #ECE5DD; /* WhatsApp background color */
}

/* Style chat messages */
.chat-bubble {
    position: relative;
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Style for user's messages */
.chat-message.user {
    background-color: #DCF8C6; /* WhatsApp sender bubble color */
    margin-left: 20%;
    text-align: right;
}

/* Style for assistant's messages */
.chat-message.assistant {
    background-color: #FFFFFF; /* WhatsApp receiver bubble color */
    margin-right: 20%;
}

/* Style for chat input */
input.stTextInput {
    border-radius: 20px;
    padding: 10px;
}

/* Adjust button style to match WhatsApp's send button */
button {
    border-radius: 50%;
    height: 40px;
    width: 40px;
    padding: 0;
    background-color: #25D366; /* WhatsApp primary color */
}

/* Icons, if necessary */
.sent-icon {
    display: inline-block;
    background-image: url('sent-icon.png'); /* replace with your icon's path */
    height: 16px;
    width: 16px;
}

.delivered-icon {
    /* similar setup for other icons */
}


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
