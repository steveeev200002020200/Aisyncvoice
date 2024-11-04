import os
import threading
import speech_recognition as sr
from gtts import gTTS
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from io import BytesIO

keep_running = False
audio_file = None

def update_translation(input_lang, output_lang):
    global keep_running, audio_file

    if keep_running:
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print("Speak Now!\n")
            audio = r.listen(source)
            
            try:
                speech_text = r.recognize_google(audio, language=input_lang)
                print("You said:", speech_text)
                
                translated_text = GoogleTranslator(source=input_lang, target=output_lang).translate(speech_text)
                print("Translated Text:", translated_text)

                # Save the translated text as audio
                audio_bytes = BytesIO()
                tts = gTTS(translated_text, lang=output_lang)
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                audio_file = audio_bytes

            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

            if keep_running:
                threading.Timer(0, update_translation, args=(input_lang, output_lang)).start()
            else:
                print("Translation stopped")

def start_translation(input_lang, output_lang):
    global keep_running
    if not keep_running:
        keep_running = True
        threading.Thread(target=update_translation, args=(input_lang, output_lang)).start()
        print('Translation started successfully.')
    else:
        print('Translation is already running.')

def stop_translation():
    global keep_running
    if keep_running:
        keep_running = False
        print('Translation stopped successfully.')
    else:
        print('Translation is not running.')

def play_audio(audio_bytes):
    sound = AudioSegment.from_file(audio_bytes, format="mp3")
    os.system("start /min audio.mp3")
    sound.export("audio.mp3", format="mp3")
    os.system("start audio.mp3")

if __name__ == '__main__':
    input_lang = "en"  # Set input language
    output_lang = "hi"  # Set output language

    start_translation(input_lang, output_lang)

    # Let the translation run for some time
    input("Press Enter to stop translation and play audio...\n")
    stop_translation()

    if audio_file:
        play_audio(audio_file)