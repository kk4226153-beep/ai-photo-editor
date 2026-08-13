import os
from flask import Flask, render_template, request, jsonify
import replicate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = '/tmp' if os.environ.get('VERCEL') else 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/enhance-hd', methods=['POST'])
def enhance_hd():
    temp_path = None
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        image_file = request.files['image']
        temp_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(temp_path)
        
        with open(temp_path, "rb") as file_obj:
            output = replicate.run(
                "nightmareai/real-esrgan:42fe04a28c4e0300ed5d14e58f9608711050012cef22b5763234430f150f850b",
                input={"image": file_obj}
            )
        
        result_url = output[0] if isinstance(output, list) else str(output)
        return jsonify({'success': True, 'result_url': result_url})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/edit-text', methods=['POST'])
def edit_text():
    temp_path = None
    try:
        if 'image' not in request.files or 'prompt' not in request.form:
            return jsonify({'success': False, 'error': 'Image and prompt required'})
        
        image_file = request.files['image']
        prompt = request.form['prompt']
        
        temp_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(temp_path)
        
        with open(temp_path, "rb") as file_obj:
            output = replicate.run(
                "timbrooks/instruct-pix2pix:30c1d0b916a6f8ef080614f2457e7c08739f73f6b0f33d43f9696ad22e9e6231",
                input={
                    "image": file_obj,
                    "prompt": prompt,
                    "num_inference_steps": 20
                }
            )
        
        result_url = output[0] if isinstance(output, list) else str(output)
        return jsonify({'success': True, 'result_url': result_url})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True)