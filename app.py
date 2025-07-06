from flask import Flask, render_template, request, send_file, jsonify, g, session, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
import tempfile

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 🔒 Replace with a secure key

DATABASE = "users.db"

# --- Database setup ---
def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect(DATABASE)
    return g._database

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        db.commit()

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")


    
@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        return render_template("dashboard.html", username=session['username'])
    else:
        return redirect(url_for('login'))


@app.route("/merge")
def merge_page():
    return render_template("merge.html")

@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("pdfs")
    filename = request.form.get("filename", "merged.pdf")
    filename = secure_filename(filename)
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    merger = PdfMerger()
    for file in files:
        merger.append(file)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(temp_file.name)
    merger.close()

    return send_file(temp_file.name, as_attachment=True, download_name=filename)

@app.route("/split")
def split_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("split.html", username=session['username'])

@app.route("/organize")
def organize_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("organize.html", username=session['username'])


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row and row[0] == password:
        session['username'] = username  # 🔐 store login
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    password_confirm = data.get("password_confirm", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"})
    if password != password_confirm:
        return jsonify({"success": False, "message": "Passwords do not match"})

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return jsonify({"success": True, "message": "Registration successful"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already taken"})

@app.route("/logout")
def logout():
    session.pop('username', None)  # 🔓 remove login
    return redirect(url_for('index'))

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
