from flask import Flask

app = Flask(__name__)

# Define your routes and other Flask code here...

if __name__ == "__main__":
    # Run Flask on port 5001 instead of the default port 5000
    app.run(port=5001)
