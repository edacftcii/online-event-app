import sqlite3

# Veritabanını oluştur ve bağlan
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Kullanıcılar tablosu
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)
""")

# Etkinlikler tablosu
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT
)
""")

# Yorumlar tablosu (Stored XSS için)
cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    username TEXT,
    content TEXT
)
""")

# Örnek etkinlik verilerini sıfırla ve ekle
cursor.execute("DELETE FROM events")
cursor.execute("INSERT INTO events (title, location, description) VALUES ('Müzik Festivali', 'İstanbul', 'Açık hava konseri')")
cursor.execute("INSERT INTO events (title, location, description) VALUES ('Yaz Kampı', 'Antalya', 'Gönüllü gençlik kampı')")
cursor.execute("INSERT INTO events (title, location, description) VALUES ('Tiyatro Gecesi', 'İzmir', 'Komedi oyunu')")

conn.commit()
conn.close()
