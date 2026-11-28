from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Expanded Database with all major crops and regional names
CROP_DATABASE = {
    "wheat": {"price": 2450, "hi": "गेहूं", "mr": "गहू", "te": "గోధుమ", "ta": "கோதுமை", "bn": "গম", "gu": "ઘઉં", "pa": "ਕਣਕ"},
    "gehu": {"price": 2450, "hi": "गेहूं", "mr": "गहू", "te": "గోధుమ", "ta": "கோதுமை", "bn": "গম", "gu": "ઘઉં", "pa": "ਕਣਕ"},
    "onion": {"price": 1850, "hi": "प्याज", "mr": "कांदा", "te": "ఉల్లిపాయ", "ta": "வெங்காயம்", "bn": "পেঁয়াজ", "gu": "ડુંગળી", "pa": "ਪਿਆਜ਼"},
    "kanda": {"price": 1850, "hi": "प्याज", "mr": "कांदा", "te": "ఉల్లిపాయ", "ta": "வெங்காயம்", "bn": "পেঁয়াজ", "gu": "ડુંગળી", "pa": "ਪਿਆਜ਼"},
    "rice": {"price": 3100, "hi": "चावल", "mr": "तांदूळ", "te": "బియ్యం", "ta": "அரிசி", "bn": "চাল", "gu": "ચોખા", "pa": "ਚੌਲ"},
    "chawal": {"price": 3100, "hi": "चावल", "mr": "तांदूळ", "te": "బియ్యం", "ta": "அரிசி", "bn": "চাল", "gu": "ચોખા", "pa": "ਚੌਲ"},
    "tomato": {"price": 1400, "hi": "टमाटर", "mr": "टोमॅटो", "te": "టమోటా", "ta": "தக்காளி", "bn": "টমেটো", "gu": "ટામેટા", "pa": "ਟਮਾਟਰ"},
    "potato": {"price": 1200, "hi": "आलू", "mr": "बटाटा", "te": "బంగాళాదుంప", "ta": "உருளைக்கிழங்கு", "bn": "আলু", "gu": "બટાકા", "pa": "ਆਲੂ"},
    "cotton": {"price": 7200, "hi": "कपास", "mr": "कापूस", "te": "పత్తి", "ta": "பருத்தி", "bn": "তুলা", "gu": "કપાસ", "pa": "ਕਪਾਹ"},
    "sugarcane": {"price": 350, "hi": "गन्ना", "mr": "ऊस", "te": "చెరకు", "ta": "கரும்பு", "bn": "আখ", "gu": "શેરડી", "pa": "ਗੰਨਾ"},
    "soybean": {"price": 4600, "hi": "सोयाबीन", "mr": "सोयाबीन", "te": "సోయాబీన్", "ta": "சோயாபீன்", "bn": "সয়াবিন", "gu": "સોયાબીન", "pa": "ਸੋਇਆਬੀਨ"},
    "mustard": {"price": 5400, "hi": "सरसों", "mr": "मोहरी", "te": "ఆవాలు", "ta": "கடுகு", "bn": "সরিষা", "gu": "સરસવ", "pa": "ਸਰੋਂ"},
    "groundnut": {"price": 6300, "hi": "मूंगफली", "mr": "भुईमूग", "te": "వేరుశనగ", "ta": "நிலக்கடலை", "bn": "চিনাবাদাম", "gu": "મગફળી", "pa": "ਮੂੰਗਫਲੀ"}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/voice', methods=['POST'])
def process_voice():
    data = request.json
    user_text = data.get('text', '').lower()
    user_role = data.get('role', 'seller') # seller or buyer
    
    response_text = "I did not understand. Please say the crop name again."
    crop_found = None
    price = 0
    local_crop_name = ""
    detected_lang = "en"

    # 1. Detect Crop and Language
    for key, details in CROP_DATABASE.items():
        # Check if the English name or any regional name is in the user's speech
        if key in user_text:
            crop_found = key.capitalize()
            price = details["price"]
            local_crop_name = crop_found
            break
        
        # Check regional names to auto-detect language
        for lang_code in ["hi", "mr", "te", "ta", "bn", "gu", "pa"]:
            if details.get(lang_code) and details[lang_code] in user_text:
                crop_found = key.capitalize()
                price = details["price"]
                local_crop_name = details[lang_code]
                detected_lang = lang_code # We figured out their language!
                break
        if crop_found: break

    if not crop_found:
        # Fallback if crop not found
        if "bechna" in user_text or "vikayche" in user_text or "sell" in user_text:
             detected_lang = "hi" if "bechna" in user_text else "mr"
             return jsonify({"status": "error", "spoken_response": "Crop not found. Please try again.", "crop_display": "", "price": 0})

    # 2. Generate Response based on Role and Detected Language
    if crop_found:
        if user_role == "seller":
            if detected_lang == "hi": response_text = f"{local_crop_name} का आपके नज़दीकी मंडी में भाव {price} रुपये है। खरीदार ढूंढ रहे हैं..."
            elif detected_lang == "mr": response_text = f"{local_crop_name} चा तुमच्या जवळच्या मंडईत भाव {price} रुपये आहे. खरेदीदार शोधत आहोत..."
            elif detected_lang == "te": response_text = f"{local_crop_name} ధర మీ సమీప మార్కెట్లో {price} రూపాయలు. కొనుగోలుదారుని వెతుకుతున్నాము..."
            else: response_text = f"The price for {local_crop_name} is {price} rupees. Connecting you to a buyer..."
        else: # Buyer
            if detected_lang == "hi": response_text = f"आप {local_crop_name} खरीदना चाहते हैं। हम आपको {price} रुपये प्रति क्विंटल पर किसान से जोड़ रहे हैं।"
            elif detected_lang == "mr": response_text = f"तुम्हाला {local_crop_name} खरेदी करायचे आहे. आम्ही तुम्हाला {price} रुपये प्रति क्विंटल दराने शेतकऱ्याशी जोडत आहोत."
            else: response_text = f"You want to buy {local_crop_name}. Connecting you to a farmer at {price} rupees per quintal..."
    
    return jsonify({
        "status": "success",
        "spoken_response": response_text,
        "crop_display": local_crop_name,
        "price": price if crop_found else None,
        "detected_lang": detected_lang
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
