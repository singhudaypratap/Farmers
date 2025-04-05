from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
genai.configure(api_key="AIzaSyCdHvM6djoFfXcAHcfxrPH5on6d7fZ5cqA") # Gemini API Key

model = genai.GenerativeModel("gemini-1.5-flash")

conversation_history = []
last_message_time = time.time()

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history, last_message_time

    user_message = request.json.get("message", "").strip()
    
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    # Auto-clear history if inactive for 5 minutes (300 seconds)
    current_time = time.time()
    if current_time - last_message_time > 300:
        conversation_history.clear()

    last_message_time = current_time  # Update timestamp

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})

    # Define the prompt with history
    prompt = f"Conversation history: {conversation_history}. Reply briefly in the same tone and language as '{user_message}'. If explanation is needed, keep it short and to point and related to farming. If unrelated, respond with 'Please enter a farming-related prompt.'"

    try:
        # Call Gemini model to generate response
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            bot_reply = response.text.strip()
        else:
            bot_reply = "Sorry, I couldn't understand that."

        # Add bot response to conversation history
        conversation_history.append({"role": "assistant", "content": bot_reply})

        return jsonify({"reply": bot_reply})
    
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({"reply": "Error processing request."})

if __name__ == '__main__':
    app.run(debug=True)
