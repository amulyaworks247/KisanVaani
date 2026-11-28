from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Added actual scripts (Telugu, Hindi, Marathi, English) for accurate detection
CROP_DATABASE = {
    "wheat": {"price": 2450, "names": ["gehu", "गेहूं", "గోధుమ", "गहू"], "lang_map": {"గోధుమ": "te", "गेहूं": "hi", "गहू": "mr", "gehu": "hi"}},
    "onion": {"price": 1850, "names": ["onion", "pyaz", "प्याज", "ఉల్లిపాయ", "कांदा", "kanda"], "lang_map": {"ఉల్లిపాయ": "te", "प्याज": "hi", "कांदा": "mr", "kanda": "mr"}},
    "rice": {"price": 3100, "names": ["rice", "chawal", "चावल", "బియ్యం", "तांदूळ"], "lang_map": {"బియ్యం": "te", "चावल": "hi", "तांदूळ": "mr"}},
    "tomato": {"price": 1400, "names": ["tomato", "टमाटर", "టమోటా", "टोमॅटो"], "lang_map": {"టమోటా": "te", "टमाटर": "hi", "टोमॅटो": "mr"}},
    "cotton": {"price": 7200, "names": ["cotton", "kapas", "कपास", "పత్తి", "कापूस"], "lang_map": {"పత్తి": "te", "कपास": "hi", "कापूस": "mr"}}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/voice', methods=['POST'])
def process_voice():
    data = request.json
    user_text = data.get('text', '')
    user_role = data.get('role', 'seller')
    
    response_text = "I did not understand. Please say the crop name again."
    crop_found = None
    price = 0
    local_crop_name = ""
    detected_lang = "en"

    # 1. Search for the crop in the text
    for key, details in CROP_DATABASE.items():
        for name in details["names"]:
            if name in user_text:
                crop_found = key.capitalize()
                price = details["price"]
                local_crop_name = name
                # Identify the language based on the matched name
                if name in details["lang_map"]:
                    detected_lang = details["lang_map"][name]
                elif name in ["gehu", "pyaz", "chawal", "kapas"]:
                    detected_lang = "hi" # If spoken in English letters (Hinglish)
                break
        if crop_found: break

    # 2. Generate Response
    if crop_found:
        if user_role == "seller":
            if detected_lang == "te": response_text = f"{local_crop_name} ధర మీ సమీప మార్కెట్లో {price} రూపాయలు. కొనుగోలుదారుని వెతుకుతున్నాము..."
            elif detected_lang == "hi": response_text = f"{local_crop_name} का आपके नज़दीकी मंडी में भाव {price} रुपये है। खरीदार ढूंढ रहे हैं..."
            elif detected_lang == "mr": response_text = f"{local_crop_name} चा तुमच्या जवळच्या मंडईत भाव {price} रुपये आहे. खरेदीदार शोधत आहोत..."
            else: response_text = f"The price for {local_crop_name} is {price} rupees. Connecting you to a buyer..."
        else: # Buyer
            if detected_lang == "te": response_text = f"మీరు {local_crop_name} కొనాలనుకుంటున్నారు. మేము మిమ్మల్ని రైతుతో కలుపుతున్నాము."
            elif detected_lang == "hi": response_text = f"आप {local_crop_name} खरीदना चाहते हैं। हम आपको किसान से जोड़ रहे हैं।"
            elif detected_lang == "mr": response_text = f"तुम्हाला {local_crop_name} खरेदी करायचे आहे. आम्ही तुम्हाला शेतकऱ्याशी जोडत आहोत."
            else: response_text = f"You want to buy {local_crop_name}. Connecting you to a farmer..."
    else:
        # If we couldn't find the crop, check what language they were likely speaking
        if any(char in user_text for char in ["గ", "ధ", "ర"]): detected_lang = "te"
        elif any(char in user_text for char in ["क", "ग", "ह"]): detected_lang = "hi"

    return jsonify({
        "status": "success",
        "spoken_response": response_text,
        "crop_display": local_crop_name,
        "price": price if crop_found else None,
        "detected_lang": detected_lang
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
