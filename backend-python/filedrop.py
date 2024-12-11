# Flask and Django integrated file upload script
# Save this as a Python file (e.g., `app.py`) and install required packages before running.

# Import Flask for file upload
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import MySQLdb

# Import Django for ORM and database management
import django
from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage

# Initialize Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'your_database',  # Replace with your database name
            'USER': 'your_user',      # Replace with your MySQL username
            'PASSWORD': 'your_password',  # Replace with your MySQL password
            'HOST': 'localhost',     # Replace if using a different host
            'PORT': '3306',          # Replace if using a different port
        }
    },
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'file_upload_app',
    ),
)
django.setup()

# Define the File model in Django
class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_content = models.BinaryField()

# Initialize Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML Template for Drag-and-Drop Feature
drag_and_drop_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f7f7f7;
        }
        .drop-zone {
            border: 2px dashed #007bff;
            border-radius: 10px;
            width: 50%;
            padding: 20px;
            text-align: center;
            color: #555;
        }
        .drop-zone.dragover {
            background-color: #e8f7ff;
        }
    </style>
</head>
<body>
    <div class="drop-zone" id="drop-zone">
        Drag and drop your file here or <b>click to upload</b>
        <form id="file-form" method="POST" enctype="multipart/form-data" style="display: none;">
            <input type="file" id="file-input" name="file">
        </form>
    </div>
    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                uploadFile(files[0]);
            }
        });

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData,
            }).then(response => response.json()).then(data => {
                alert(data.message);
            }).catch(error => {
                console.error('Error uploading file:', error);
            });
        }
    </script>
</body>
</html>
"""

# Route for the Drag-and-Drop UI
@app.route('/')
def index():
    return drag_and_drop_html

# Route for handling file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save file to MySQL using Django ORM
        with open(file_path, 'rb') as f:
            file_content = f.read()
        uploaded_file = UploadedFile(file_name=filename, file_content=file_content)
        uploaded_file.save()

        # Optionally, remove the file after saving to DB
        os.remove(file_path)

        return jsonify({"message": "File uploaded and saved successfully!"})

    return jsonify({"message": "No file uploaded!"}), 400

# Run Flask application
if __name__ == '__main__':
    app.run(debug=True)