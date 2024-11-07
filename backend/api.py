from flask import Flask, request, jsonify, send_file, after_this_request
from openai import OpenAI
import shutil
import glob
import time
import os
import yaml
import argparse
import sys

app = Flask(__name__)

UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploadFile', methods=['POST'])
def upload_file():
    # Check if the file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file was uploaded
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Save the uploaded file temporarily
    temp_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_path)

    try:
        # Upload the file to the assistant’s vector store
        assistant = client.beta.assistants.retrieve("asst_Wk1Ue0iDYkhbdiXXDPPJsvAV")

        with open(temp_path, "rb") as f:
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id='vs_qUspcB7VllWXM4z7aAEdIK9L', files=[f]
            )

        # Check upload status
        if file_batch.status != "completed":
            return jsonify({"error": "File upload failed"}), 500

        # Clean up the temporary file after upload
        os.remove(temp_path)

        return jsonify({"response": "File uploaded successfully"}), 200
    
    except Exception as e:
        # Handle exceptions and send a response
        return jsonify({"error": str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        assistant = client.beta.assistants.retrieve("asst_Wk1Ue0iDYkhbdiXXDPPJsvAV")
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        messages_str = messages.data[0].content[0].text.value
        return jsonify({"response": messages_str}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



if __name__ == '__main__':

    client = OpenAI()

    app.run(host='0.0.0.0', port=5500)
