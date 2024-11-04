from flask import Flask, request, jsonify, send_file
from io import BytesIO
import threading
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})  # Allow CORS for requests from http://127.0.0.1:5500

keep_running = False
audio_file = None
audio_ready = False  # Flag to indicate when audio file is ready

# Define your functions and routes here...

if __name__ == '__main__':
    app.run(debug=True)
