from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Simulated database of crop prices
CROP_PRICES = {
    "wheat": 2200,
    "gehu": 2200,
    "onion": 1800,
    "kanda": 1800,
    "rice": 2500,
    "chawal": 2500,
    "tomato": 1200
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/voice', methods=['POST'])
def process_voice():
    data = request.json
    user_text = data.get('text', '').lower()
    
    # Simple logic to parse the user's speech
    response_text = "I did not understand that. Please say the crop name."
    crop_found = None
    price = 0

    for crop, p in CROP_PRICES.items():
        if crop in user_text:
            crop_found = crop.capitalize()
            price = p
            break

    if crop_found:
        if "sell" in user_text or "bechna" in user_text or "vikayche" in user_text:
            response_text = f"Connecting you to a verified local buyer for {crop_found}. Please wait."
        else:
            response_text = f"The price for {crop_found} at your nearest mandi is {price} rupees per quintal."
    
    return jsonify({
        "status": "success",
        "spoken_response": response_text,
        "crop": crop_found,
        "price": price if crop_found else None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)