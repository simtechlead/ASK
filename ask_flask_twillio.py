from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import time
from openai import OpenAI

app = Flask(__name__)

def interact_with_openai(user_message):
    try:
        print("Received user message:", user_message)  # Log user message

        openai_key = os.getenv('OPENAI_KEY')
        org_ID = os.getenv('ORG_ID')

        print("Retrieving OpenAI client...")  # Log retrieval of client
        client = OpenAI(organization=org_ID, api_key=openai_key)
        assistant = client.beta.assistants.retrieve("asst_kehD6QVaQfE8FFSf3Yfyaj0l")
        
        print("Creating thread...")  # Log thread creation
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)

        print("Running assistant...")  # Log running assistant
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == 'completed':
                break
            else:
                time.sleep(1)

        print("Retrieving messages...")  # Log message retrieval
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        responses = []
        for each in messages:
            if each.role == 'assistant':
                response_text = each.content[0].text.value if isinstance(each.content, list) and hasattr(each.content[0], 'text') else str(each.content)
                print("Assistant response:", response_text)  # Log each response
                responses.append(response_text)
        return responses

    except Exception as e:
        error_message = f"Error: {e}"
        print(error_message)  # Log error
        return [error_message]

@app.route("/whatsapp-webhook", methods=['POST'])
def reply_whatsapp():
    # Parse the incoming message from WhatsApp
    incoming_msg = request.json.get('messages', [{}])[0].get('text', {}).get('body', '').strip()
    print("Incoming WhatsApp message:", incoming_msg)

    responses = interact_with_openai(incoming_msg)

    # Prepare the response data for WhatsApp Business API
    response_data = {
        "messages": [
            {"text": {"body": response}} for response in responses
        ]
    }

return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)