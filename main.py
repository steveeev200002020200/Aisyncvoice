from flask import Flask, request, jsonify, Response, send_from_directory
from io import BytesIO
import os
import tempfile
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)
CORS(app, origins='*')  # Allow requests from any origin

keep_running = False
audio_ready = False
audio_data = None

def capture_audio():
    # Function to capture audio from console
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak Now!\n")
        audio = r.listen(source)
    return audio

def update_translation(input_lang, output_lang):
    global keep_running, audio_ready, audio_data

    print("update_translation function called.")

    if keep_running:
        audio = capture_audio()

        try:
            speech_text = sr.Recognizer().recognize_google(audio, language=input_lang)
            print("Speech Recognized:", speech_text)
            translator = GoogleTranslator(source=input_lang, target=output_lang)
            translated_text = translator.translate(speech_text)
            print("Translated Text:", translated_text)

            # Generate translated audio
            tts = gTTS(text=translated_text, lang=output_lang)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            audio_data = audio_bytes.getvalue()
            audio_ready = True

        except sr.UnknownValueError as e:
            error_message = "Speech Recognition could not understand audio"
            print(error_message)
            return jsonify({'error': error_message}), 400
        except sr.RequestError as e:
            error_message = "Speech Recognition request failed: {0}".format(e)
            print(error_message)
            return jsonify({'error': error_message}), 400
        except Exception as e:
            error_message = "Error during translation: {0}".format(e)
            print(error_message)
            return jsonify({'error': error_message}), 500

    return None

@app.route('/start_translation', methods=['POST'])
def start_translation():
    global keep_running, audio_ready, audio_data
    if not keep_running:
        data = request.json
        print("Received data:", data)
        input_lang = data.get('input_lang')
        output_lang = data.get('output_lang')
        if input_lang and output_lang:
            keep_running = True
            update_translation(input_lang, output_lang)
            if audio_ready and audio_data:
                return Response(audio_data, mimetype='audio/mpeg')
            else:
                return jsonify({'error': 'Error during translation. Please try again later.'}), 500
        else:
            return jsonify({'error': 'Input and output languages are required.'}), 400
    else:
        return jsonify({'error': 'Translation is already running.'}), 400

@app.route('/stop_translation', methods=['POST'])
def stop_translation():
    global keep_running, audio_ready, audio_data
    if keep_running:
        keep_running = False
        audio_ready = False
        audio_data = None
        return jsonify({'message': 'Translation stopped successfully.'}), 200
    else:
        return jsonify({'error': 'Translation is not running.'}), 400

app.config['UPLOAD_FOLDER'] = 'uploads'
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def update_translation1(input_lang, output_lang, audio_data):
    try:
        # Convert M4A to WAV using pydub
        audio = AudioSegment.from_file(audio_data, format="m4a")
        wav_file = tempfile.NamedTemporaryFile(delete=False)
        wav_file_path = wav_file.name + '.wav'
        audio.export(wav_file_path, format='wav')
        wav_file.close()

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_path) as source:
            audio = recognizer.record(source)

        speech_text = recognizer.recognize_google(audio, language=input_lang)
        print("Speech Recognized:", speech_text)
        translator = GoogleTranslator(source=input_lang, target=output_lang)
        translated_text = translator.translate(speech_text)
        print("Translated Text:", translated_text)

        # Generate translated audio
        tts = gTTS(text=translated_text, lang=output_lang)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        # Clean up temporary WAV file
        os.remove(wav_file_path)

        return audio_bytes.getvalue()

    except sr.UnknownValueError:
        error_message = "Speech Recognition could not understand audio"
        print(error_message)
        return jsonify({'error': error_message}), 400
    except sr.RequestError as e:
        error_message = "Speech Recognition request failed: {0}".format(e)
        print(error_message)
        return jsonify({'error': error_message}), 400
    except Exception as e:
        error_message = "Error during translation: {0}".format(e)
        print(error_message)
        return jsonify({'error': error_message}), 500

@app.route('/translate', methods=['POST'])
def translate():
    src_lang = request.form.get('lang_one')
    dest_lang = request.form.get('lang_two')
    recording = request.files['record']

    if not src_lang or not dest_lang or not recording:
        return jsonify({'error': 'Missing required parameters.'}), 400

    filename = secure_filename(recording.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    recording.save(filepath)

    translated_audio = update_translation1(src_lang, dest_lang, filepath)
    if isinstance(translated_audio, bytes):
        return Response(translated_audio, mimetype='audio/mpeg')
    else:
        return translated_audio

@app.route('/translated_audio/<filename>', methods=['GET'])
def download_translated_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(port=5500)