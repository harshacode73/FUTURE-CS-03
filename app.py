from flask import Flask, request, render_template, send_file, redirect, url_for, session
import os
from encryption import encrypt_file, decrypt_file
from dotenv import load_dotenv

load_dotenv()
import os

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

print("Loaded from .env:", USERNAME, PASSWORD)  # Debug print

app = Flask(__name__)
app.secret_key = 'mysecretflasksessionkey'

UPLOAD_FOLDER = 'uploads'
DECRYPTED_FOLDER = 'decrypted'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == USERNAME and pwd == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return "Login failed"
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            data = file.read()
            encrypted = encrypt_file(data)
            filepath = os.path.join(UPLOAD_FOLDER, filename + '.enc')
            with open(filepath, 'wb') as f:
                f.write(encrypted)
            return f'Encrypted and saved: {filename}.enc'
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    encrypted_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted = decrypt_file(encrypted_data)
    decrypted_path = os.path.join(DECRYPTED_FOLDER, filename.replace('.enc', ''))
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted)
    return send_file(decrypted_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5050)  # using port 5050 to avoid port conflict
