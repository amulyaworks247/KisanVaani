from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

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
    final_lang = gps_lang # Default to GPS

    # 1. THE LANGUAGE PIVOT: Detect script overrides GPS
    if re.search(r'[\u0C00-\u0C7F]', user_text): final_lang = "te" # Telugu
    elif re.search(r'[\u0B80-\u0BFF]', user_text): final_lang = "ta" # Tamil
    elif re.search(r'[\u0C80-\u0CFF]', user_text): final_lang = "kn" # Kannada
    elif re.search(r'[\u0D00-\u0D7F]', user_text): final_lang = "ml" # Malayalam
    elif re.search(r'[\u0980-\u09FF]', user_text): final_lang = "bn" # Bengali
    elif re.search(r'[\u0A80-\u0AFF]', user_text): final_lang = "gu" # Gujarati
    elif re.search(r'[\u0900-\u097F]', user_text): final_lang = "hi" # Hindi/Marathi

    # 2. FIND THE CROP
    for key, details in CROP_DATABASE.items():
        for name in details["names"]:
            if name in user_text:
                crop_found = key.capitalize()
                price = details["price"]
                local_crop_name = name
                break
        if crop_found: break

    # 3. GENERATE RESPONSE
    if crop_found:
        if user_role == "seller":
            if final_lang == "te": response_text = f"{local_crop_name} ధర {price} రూపాయలు. ఈ ధరతో మీరు సంతృప్తి చెందారా?"
            elif final_lang == "ta": response_text = f"{local_crop_name} விலை {price} ரூபாய். இந்த விலையில் நீங்கள் திருப்தியடைகிறீர்களா?"
            elif final_lang == "kn": response_text = f"{local_crop_name} ಬೆಲೆ {price} ರೂಪಾಯಿ. ಈ ಬೆಲೆಯಿಂದ ನೀವು ತೃಪ್ತರಾಗಿದ್ದೀರಾ?"
            elif final_lang == "ml": response_text = f"{local_crop_name} വില {price} രൂപയാണ്. ഈ വിലയിൽ നിങ്ങൾക്ക് തൃപ്തിയാണോ?"
            elif final_lang == "hi": response_text = f"{local_crop_name} का भाव {price} रुपये है। क्या आप इस कीमत से खुश हैं?"
            elif final_lang == "mr": response_text = f"{local_crop_name} चा भाव {price} रुपये आहे. तुम्हाला हा दर मान्य आहे का?"
            else: response_text = f"The price for {local_crop_name} is {price} rupees. Are you happy with this price?"
        else:
            if final_lang == "te": response_text = f"మీరు {local_crop_name} కొనాలనుకుంటున్నారు. మేము రైతుతో కలుపుతున్నాము."
            elif final_lang == "ta": response_text = f"நீங்கள் {local_crop_name} வாங்க விரும்புகிறீர்கள். விவசாயியுடன் இணைக்கிறோம்."
            elif final_lang == "kn": response_text = f"ನೀವು {local_crop_name} ಖರೀದಿಸಲು ಬಯಸುತ್ತೀರಿ. ರೈತರೊಂದಿಗೆ ಸಂಪರ್ಕಿಸುತ್ತಿದ್ದೇವೆ."
            elif final_lang == "ml": response_text = f"നിങ്ങൾക്ക് {local_crop_name} വാങ്ങണം. കർഷകനുമായി ബന്ധിപ്പിക്കുന്നു."
            elif final_lang == "hi": response_text = f"आप {local_crop_name} खरीदना चाहते हैं। किसान से जोड़ रहे हैं।"
            elif final_lang == "mr": response_text = f"तुम्हाला {local_crop_name} खरेदी करायचे आहे. शेतकऱ्याशी जोडत आहोत."
            else: response_text = f"You want to buy {local_crop_name}. Connecting you to a farmer..."
    else:
        if final_lang == "te": response_text = "దయచేసి పంట పేరు చెప్పండి."
        elif final_lang == "ta": response_text = "பயிர் பெயரைச் சொல்லுங்கள்."
        elif final_lang == "kn": response_text = "ದಯವಿಟ್ಟು ಬೆಳೆ ಹೆಸರನ್ನು ಹೇಳಿ."
        elif final_lang == "ml": response_text = "വിളയുടെ പേര് പറയുക."
        elif final_lang == "hi": response_text = "कृपया फसल का नाम बताएं।"
        elif final_lang == "mr": response_text = "कृपया पिकाचे नाव सांगा."
        else: response_text = "Please say the crop name."

    return jsonify({
        "status": "success",
        "spoken_response": response_text,
        "crop_display": local_crop_name if crop_found else "Not Found",
        "price": price if crop_found else 0,
        "detected_lang": final_lang
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
