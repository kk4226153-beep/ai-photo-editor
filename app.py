import os
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import replicate

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file upload

def image_to_data_uri(file_storage):
    """Uploaded image file ko base64 data URI me convert karta hai."""
    file_bytes = file_storage.read()
    encoded = base64.b64encode(file_bytes).decode('utf-8')
    mime_type = file_storage.content_type or 'image/png'
    return f"data:{mime_type};base64,{encoded}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/enhance-hd', methods=['POST'])
def enhance_hd():
    """Real-ESRGAN model ke zariye photo ko HD banata hai."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Koi image select nahi ki gayi'}), 400
        
        file = request.files['image']
        data_uri = image_to_data_uri(file)

        output = replicate.run(
            "nightmareai/real-esrgan:42203233982c4e511c7870125f424410808a3264964627050302b11561570773",
            input={
                "image": data_uri,
                "upscale": 2,
                "face_enhance": True
            }
        )
        return jsonify({'success': True, 'result_url': output})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-text', methods=['POST'])
def edit_text():
    """InstructPix2Pix model ke zariye text prompt ke mutabiq photo edit karta hai."""
    try:
        if 'image' not in request.files or 'prompt' not in request.form:
            return jsonify({'error': 'Image ya Text Prompt missing hai'}), 400
        
        file = request.files['image']
        prompt = request.form['prompt']
        data_uri = image_to_data_uri(file)

        output = replicate.run(
            "timothybrooks/instruct-pix2pix:30c1d0b916a6f8ef220d710812582104278a2e5845c47a5183815c32e92c2a05",
            input={
                "image": data_uri,
                "prompt": prompt,
                "num_inference_steps": 30,
                "image_guidance_scale": 1.5
            }
        )
        
        result_url = output[0] if isinstance(output, list) else output
        return jsonify({'success': True, 'result_url': result_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)