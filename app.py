from flask import Flask, request, render_template_string
import base64
import requests
import json  # Import json for pretty printing



app = Flask(__name__)

# OpenAI API Key
api_key = ""

# Function to encode the image
@app.route('/')
def home():
    # Basic form for file upload
    return '''
    <form method="post" action="/analyze" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit">
    </form>
    '''

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    if file:
        base64_image = base64.b64encode(file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": "Can you return a list of ingredients in the fridge as JSON?"
                }, {
                    "type": "image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }]
            }],
            "max_tokens": 300
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        # Extract the ingredients text from the response
        if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
            content_text = response_data['choices'][0]['message']['content']
            # Extract the JSON string from the content
            json_start = content_text.find('{')
            json_end = content_text.rfind('}') + 1
            ingredients_json = content_text[json_start:json_end]
            
            return ingredients_json
        else:
            return "Error: Unable to extract ingredients"

if __name__ == '__main__':
    app.run(debug=True)