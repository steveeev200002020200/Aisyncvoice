from app import app
from flask import jsonify

@app.route('/start_translation')
def start_translation():
    # Your translation logic here
    return jsonify({'message': 'Translation started'})
