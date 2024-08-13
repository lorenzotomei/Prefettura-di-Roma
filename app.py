from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Assicurati che la cartella di upload esista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_link():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        link = request.form['link']
        title = request.form['title']
        category = request.form['category']
        office = request.form['office']
        if link and title:
            link_data = {
                'link': link,
                'title': title,
                'category': category,
                'office': office,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'links.json'), 'a') as f:
                f.write(json.dumps(link_data) + '\n')
            return redirect(url_for('list_files'))
    return render_template('upload.html')

@app.route('/files')
def list_files():
    documents = []
    decrees = []
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'links.json')):
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'links.json'), 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    timestamp = data.get('timestamp', 'N/A')
                    category = data.get('category', 'documento')  # Default to 'documento' if 'category' is missing
                    office = data.get('office', 'N/A')  # Default to 'N/A' if 'office' is missing
                    
                    if category == 'documento':
                        documents.append({**data, 'timestamp': timestamp, 'office': office})
                    elif category == 'decreto':
                        decrees.append({**data, 'timestamp': timestamp, 'office': office})
                except json.JSONDecodeError:
                    continue

    # Ordinamento per data di caricamento
    documents = sorted(documents, key=lambda x: x['timestamp'], reverse=True)
    decrees = sorted(decrees, key=lambda x: x['timestamp'], reverse=True)

    return render_template('files.html', documents=documents, decrees=decrees)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'prefetturaromarp':
            session['logged_in'] = True
            return redirect(url_for('upload_link'))
        else:
            flash('Credenziali non valide, riprova.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

