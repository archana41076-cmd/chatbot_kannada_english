import json
from flask import Flask, render_template, request, make_response
import nltk
from nltk.tokenize import word_tokenize

app = Flask(__name__)

# Load responses from the appropriate language file
def load_responses(language='english'):
    filename = f'responses_{language}.json'  # Choose based on the selected language
    try:
        with open(filename, 'r', encoding='utf-8') as f:  # Specify UTF-8 encoding
            return json.load(f)
    except FileNotFoundError:
        return {}

# Store chat history
messages = []

# Initialize NLTK tokenization
nltk.download('punkt')

@app.route("/", methods=["GET"])
def home():
    # Read the language preference from cookies, default to 'english' if not set
    language = request.cookies.get('language', 'english')
    responses = load_responses(language)
    return render_template("index.html", messages=messages, language=language)

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.form['user_message']
    language = request.cookies.get('language', 'english')  # Get selected language
    
    responses = load_responses(language)  # Load the corresponding language responses
    
    # Match user input to predefined responses using tokenization
    def get_response(user_message):
        user_message = user_message.lower()
        tokens = word_tokenize(user_message)  # Tokenize the user input
        
        # Match each token in user input with predefined responses
        for token in tokens:
            if token in responses:
                return responses[token]  # Return the matching response
        
        # Default response in the selected language if no match is found
        if language == 'kannada':
            return "ಕ್ಷಮಿಸಿ, ನಾನು ಅದನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಂದು ಪ್ರಶ್ನೆ ಕೇಳಿ."
        return "I'm sorry, I couldn't find an answer to that.Please be specific about your question"
    
    bot_response = get_response(user_message)
    
    # Append user and bot messages to the chat history
    messages.append((user_message, "user-message"))
    messages.append((bot_response, "bot-message"))
    
    # Save the selected language in a cookie for future requests
    resp = make_response(render_template("index.html", messages=messages, language=language))
    resp.set_cookie('language', language)  # Save the language choice in a cookie
    
    return resp

# Route to change language preference
@app.route("/change_language/<language>", methods=["GET"])
def change_language(language):
    if language not in ['english', 'kannada']:
        language = 'english'  # Default to English if invalid language is selected
    
    # Save the language in a cookie
    resp = make_response(render_template("index.html", messages=messages, language=language))
    resp.set_cookie('language', language)  # Save the language choice in a cookie
    
    return resp

if __name__ == "__main__":
    app.run(debug=True)
