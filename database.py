import sqlite3, hashlib
from pathlib import Path
DB = Path(__file__).parent / "campus.db"

def conn():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    c=conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
      role TEXT NOT NULL, department TEXT, bio TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, receiver_id INTEGER,
      message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS groups(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_by INTEGER,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS group_members(
      group_id INTEGER, user_id INTEGER, UNIQUE(group_id,user_id));
    CREATE TABLE IF NOT EXISTS group_messages(
      id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER, sender_id INTEGER,
      message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS announcements(
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT,
      posted_by INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS complaints(
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, title TEXT,
      description TEXT, category TEXT, priority TEXT, status TEXT DEFAULT 'Pending',
      assigned_to INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT,
      event_date TEXT, location TEXT, created_by INTEGER,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS event_registrations(
      id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, user_id INTEGER,
      UNIQUE(event_id,user_id));
    CREATE TABLE IF NOT EXISTS documents(
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, filename TEXT,
      department TEXT, uploaded_by INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS ai_history(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, question TEXT,
      answer TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """)
    # Demo admin account
    if not c.execute("SELECT 1 FROM users WHERE email=?",("admin@campus.com",)).fetchone():
        c.execute("INSERT INTO users(name,email,password,role,department) VALUES(?,?,?,?,?)",
                  ("Campus Admin","admin@campus.com",hash_password("admin123"),"admin","Administration"))
    c.commit(); c.close()

def create_user(name,email,password,role,department):
    try:
        c=conn(); c.execute("INSERT INTO users(name,email,password,role,department) VALUES(?,?,?,?,?)",
                            (name,email,hash_password(password),role,department))
        c.commit(); c.close(); return True,"Account created. Please login."
    except sqlite3.IntegrityError: return False,"Email already exists."

def authenticate(email,password):
    c=conn(); r=c.execute("SELECT * FROM users WHERE email=? AND password=?",
                           (email,hash_password(password))).fetchone(); c.close()
    return dict(r) if r else None

def get_user(uid):
    c=conn(); r=c.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone(); c.close()
    return dict(r) if r else None

def rows(sql,args=()):
    c=conn(); r=[dict(x) for x in c.execute(sql,args).fetchall()]; c.close(); return r

def one(sql,args=()):
    c=conn(); r=c.execute(sql,args).fetchone(); c.close(); return dict(r) if r else None

def execute(sql,args=()):
    c=conn(); cur=c.execute(sql,args); c.commit(); x=cur.lastrowid; c.close(); return x
