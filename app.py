from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, session, send_file, make_response
import sqlite3
import os
import requests
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# Dosya yükleme dizini
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Admin Paneli (Yetki kontrolsüz versiyon için yorum satırı altına alabilirsin)
@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return "Yetkisiz erişim!", 403
    return render_template("admin.html")

# Ana Sayfa
@app.route("/")
def index():
    return render_template("index.html")

# Kayıt Ol

# Kayıt Ol
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Bu kullanıcı adı zaten kayıtlı."
    return render_template("register.html")

# Giriş Yap
@app.route("/login", methods=["GET", "POST"])
# def login():
  #   if request.method == "POST":
   #      username = request.form["username"]
       #  password = request.form["password"]
     #    conn = get_db()
     #   user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
     #   user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
     #   if user and check_password_hash(user["password"], password):
     #       session["username"] = user["username"]
     #       session["is_admin"] = user["is_admin"]
     #       return redirect("/")
     #   else:
     #       return "Kullanıcı adı veya parola yanlış!"
  #  return render_template("login.html")

#sorunlu hali 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
         session["username"] = user["username"]
         session["is_admin"] = user["is_admin"]
        return redirect("/")
    else: 
        return "Kullanıcı adı veya parola yanlış!"
    return render_template("login.html")

# Çıkış Yap
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Etkinlik Arama (SQL Injection Açığı)
@app.route("/search")
def search():
    query = request.args.get("q", "")
    conn = get_db()
    sql = f"SELECT * FROM events WHERE title LIKE '%{query}%'"
    results = conn.execute(sql).fetchall()
    return render_template("search.html", events=results, query=query)

# Etkinlik Detay + Yorumlar (Stored XSS)
@app.route("/event/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
    conn = get_db()
    if request.method == "POST":
        username = session.get("username", "Anonim")
        content = request.form["content"]
        conn.execute("INSERT INTO comments (event_id, username, content) VALUES (?, ?, ?)",
                     (event_id, username, content))
        conn.commit()
        return redirect(f"/event/{event_id}")
    event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    comments = conn.execute("SELECT * FROM comments WHERE event_id=?", (event_id,)).fetchall()
    return render_template("event_detail.html", event=event, comments=comments)

# Dosya Yükleme (Insecure File Upload)
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return f"Dosya yüklendi: <a href='/static/uploads/{filename}'>{filename}</a>"
    return render_template("upload.html")

# PDF Oluşturma (xhtml2pdf ile - SSRF açığı halen mevcut!)
@app.route("/generate_pdf", methods=["GET", "POST"])
def generate_pdf():
    if request.method == "POST":
        url = request.form["url"]
        try:
            response = requests.get(url)
            html = response.text

            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

            if pisa_status.err:
                return "PDF oluşturulamadı!"

            pdf_buffer.seek(0)
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='output.pdf'
            )
        except Exception as e:
            return f"Hata oluştu: {e}"
    return render_template("generate_pdf.html")

# Uygulama Başlat
if __name__ == "__main__":
    app.run(debug=True)
