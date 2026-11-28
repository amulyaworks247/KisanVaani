from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load the massive database from the JSON file
def load_database():
    with open('crops.json', 'r', encoding='utf-8') as file:
        return json.load(file)

CROP_DATABASE = load_database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/voice', methods=['POST'])
def process_voice():
    data = request.json
    user_text = data.get('text', '').lower()
    user_role = data.get('role', 'seller')
    gps_lang = data.get('gps_lang', 'en')
    
    response_text = ""
    crop_found = None
    price = 0
    local_crop_name = ""
    
    # Search the entire massive database
    for key, details in CROP_DATABASE.items():
        for name in details["names"]:
            if name in user_text:
                crop_found = key.capitalize()
                price = details["price"]
                local_crop_name = name
                break
        if crop_found: break

    # Generate Response
    if crop_found:
        if user_role == "seller":
            if gps_lang == "te": response_text = f"{local_crop_name} ధర మీ సమీప మార్కెట్లో {price} రూపాయలు. కొనుగోలుదారుని వెతుకుతున్నాము..."
            elif gps_lang == "hi": response_text = f"{local_crop_name} का आपके नज़दीकी मंडी में भाव {price} रुपये है। खरीदार ढूंढ रहे हैं..."
            elif gps_lang == "mr": response_text = f"{local_crop_name} चा तुमच्या जवळच्या मंडईत भाव {price} रुपये आहे. खरेदीदार शोधत आहोत..."
            elif gps_lang == "ta": response_text = f"{local_crop_name} விலை உங்கள் அருகிலுள்ள சந்தையில் {price} ரூபாய்."
            elif gps_lang == "kn": response_text = f"{local_crop_name} ಬೆಲೆ ನಿಮ್ಮ ಹತ್ತಿರದ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {price} ರೂಪಾಯಿ."
            elif gps_lang == "ml": response_text = f"{local_crop_name} വില നിങ്ങളുടെ അടുത്തുള്ള വിപണിയിൽ {price} രൂപയാണ്."
            else: response_text = f"The price for {local_crop_name} is {price} rupees. Connecting you to a buyer..."
        else:
            if gps_lang == "te": response_text = f"మీరు {local_crop_name} కొనాలనుకుంటున్నారు. మేము మిమ్మల్ని రైతుతో కలుపుతున్నాము."
            elif gps_lang == "hi": response_text = f"आप {local_crop_name} खरीदना चाहते हैं। हम आपको किसान से जोड़ रहे हैं।"
            elif gps_lang == "mr": response_text = f"तुम्हाला {local_crop_name} खरेदी करायचे आहे. आम्ही तुम्हाला शेतकऱ्याशी जोडत आहोत."
            elif gps_lang == "ta": response_text = f"நீங்கள் {local_crop_name} வாங்க விரும்புகிறீர்கள். விவசாயியுடன் இணைக்கிறோம்."
            elif gps_lang == "kn": response_text = f"ನೀವು {local_crop_name} ಖರೀದಿಸಲು ಬಯಸುತ್ತೀರಿ. ನಾವು ನಿಮ್ಮನ್ನು ರೈತರೊಂದಿಗೆ ಸಂಪರ್ಕಿಸುತ್ತಿದ್ದೇವೆ."
            elif gps_lang == "ml": response_text = f"നിങ്ങൾക്ക് {local_crop_name} വാങ്ങണം. ഞങ്ങൾ നിങ്ങളെ കർഷകനുമായി ബന്ധിപ്പിക്കുന്നു."
            else: response_text = f"You want to buy {local_crop_name}. Connecting you to a farmer..."
    else:
        if gps_lang == "te": response_text = "దయచేసి పంట పేరు చెప్పండి."
        elif gps_lang == "hi": response_text = "कृपया फसल का नाम बताएं।"
        elif gps_lang == "mr": response_text = "कृपया पिकाचे नाव सांगा."
        elif gps_lang == "ta": response_text = "பயிர் பெயரைச் சொல்லுங்கள்."
        elif gps_lang == "kn": response_text = "ದಯವಿಟ್ಟು ಬೆಳೆ ಹೆಸರನ್ನು ಹೇಳಿ."
        elif gps_lang == "ml": response_text = "വിളയുടെ പേര് പറയുക."
        else: response_text = "Please say the crop name."

    return jsonify({
        "status": "success",
        "spoken_response": response_text,
        "crop_display": local_crop_name if crop_found else "Not Found",
        "price": price if crop_found else 0,
        "detected_lang": gps_lang
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
