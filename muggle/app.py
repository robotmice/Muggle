import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from muggle.ai import ChatProcessor

load_dotenv()

app = Flask(__name__, static_folder='static')
processor = ChatProcessor()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field in request"}), 400
    
    user_message = data['message']
    
    response_text = processor.get_response(user_message)
    
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
