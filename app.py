import os
import base64
from flask import Flask, render_template, request, jsonify
import replicate

app = Flask(__name__, static_folder='static', template_folder='templates')

def file_to_data_uri(file_storage):
    """File Storage ko Base64 Data URI mein convert karta hai"""
    file_bytes = file_storage.read()
    base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
    mime_type = file_storage.mimetype or 'image/jpeg'
    return f"data:{mime_type};base64,{base64_encoded}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/enhance-hd', methods=['POST'])
def enhance_hd():
    try:
        api_key = os.environ.get('REPLICATE_API_TOKEN')
        if not api_key:
            return jsonify({'success': False, 'error': 'REPLICATE_API_TOKEN missing in Vercel settings!'})

        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'})
        
        image_file = request.files['image']
        image_data_uri = file_to_data_uri(image_file)
        
        client = replicate.Client(api_token=api_key)
        
        # Real-ESRGAN Model for HD Enhancement
        output = client.run(
            "nightmareai/real-esrgan:42fe04a28c4e0300ed5d14e58f9608711050012cef22b5763234430f150f850b",
            input={"image": image_data_uri}
        )
        
        result_url = output[0] if isinstance(output, list) else str(output)
        return jsonify({'success': True, 'result_url': result_url})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/edit-text', methods=['POST'])
def edit_text():
    try:
        api_key = os.environ.get('REPLICATE_API_TOKEN')
        if not api_key:
            return jsonify({'success': False, 'error': 'REPLICATE_API_TOKEN missing in Vercel settings!'})

        if 'image' not in request.files or 'prompt' not in request.form:
            return jsonify({'success': False, 'error': 'Image and prompt required'})
        
        image_file = request.files['image']
        prompt = request.form['prompt']
        
        image_data_uri = file_to_data_uri(image_file)
        
        client = replicate.Client(api_token=api_key)
        
        # Instruct-Pix2Pix Model for AI Text Editing
        output = client.run(
            "timbrooks/instruct-pix2pix:30c1d0b916a6f8ef080614f2457e7c08739f73f6b0f33d43f9696ad22e9e6231",
            input={
                "image": image_data_uri,
                "prompt": prompt,
                "num_inference_steps": 20
            }
        )
        
        result_url = output[0] if isinstance(output, list) else str(output)
        return jsonify({'success': True, 'result_url': result_url})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)