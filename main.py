from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_valid_dng(file_path):
    try:
        # Full path to exiftool executable
        exiftool_path = "C:\\Users\\npsan\\exiftool.exe"
        result = subprocess.run([exiftool_path, file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        error = result.stderr.decode()

        if error:
            print(f"ExifTool Error: {error}")
            return False

        # Log all tags for debugging purposes
        print("EXIF Tags: ", output)

        # Checking for specific Lightroom tags
        lightroom_tags = [
            'Software',
            'Make',
            # Add other specific tags you expect in a Lightroom preset
        ]

        lightroom_tag_present = any(tag in output for tag in lightroom_tags)

        if not lightroom_tag_present:
            print("Lightroom-specific tags not present.")
            return False

        # Additional checks for specific parameter values in the tags
        if 'Lightroom' in output:
            print(f"Found Lightroom tag in output")
            return True

        print("No Lightroom tags with specific values found.")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.lower().endswith('.dng'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        if is_valid_dng(file_path):
            return jsonify({'message': 'File is a valid Lightroom preset'}), 200
        else:
            return jsonify({'error': 'File is not a valid Lightroom preset'}), 400
    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    