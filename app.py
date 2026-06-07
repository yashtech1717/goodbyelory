from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "goodbye_sai_secret_key"

DATABASE = "database.db"

UPLOAD_VIDEO = "static/uploads/videos"
UPLOAD_AUDIO = "static/uploads/audio"
UPLOAD_PHOTO = "static/uploads/photos"

os.makedirs(UPLOAD_VIDEO, exist_ok=True)
os.makedirs(UPLOAD_AUDIO, exist_ok=True)
os.makedirs(UPLOAD_PHOTO, exist_ok=True)

YASH_USERNAME = "yash"
YASH_PASSWORD = "123"

LORY_USERNAME = "lory"
LORY_PASSWORD = "123"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        button_name TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS letter(
        id INTEGER PRIMARY KEY,
        content TEXT
    )
    """)

    cur.execute("""
    INSERT OR IGNORE INTO letter(id,content)
    VALUES(
        1,
        'Sai, thank you for every memory.'
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    if session["user"] == "yash":
        return redirect(url_for("admin"))

    return redirect(url_for("viewer"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == YASH_USERNAME and password == YASH_PASSWORD:

            session["user"] = "yash"
            return redirect(url_for("admin"))

        elif username == LORY_USERNAME and password == LORY_PASSWORD:

            session["user"] = "lory"
            return redirect(url_for("viewer"))

        flash("Invalid Login")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
def admin():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    conn = get_db()

    videos = conn.execute(
        "SELECT * FROM videos ORDER BY id DESC"
    ).fetchall()

    audios = conn.execute(
        "SELECT * FROM audio ORDER BY id DESC"
    ).fetchall()

    photos = conn.execute(
        "SELECT * FROM photos ORDER BY id DESC"
    ).fetchall()

    questions = conn.execute(
        "SELECT * FROM questions ORDER BY id DESC"
    ).fetchall()

    letter = conn.execute(
        "SELECT * FROM letter WHERE id=1"
    ).fetchone()

    conn.close()

    return render_template(
        "admin.html",
        videos=videos,
        audios=audios,
        photos=photos,
        questions=questions,
        letter=letter
    )


@app.route("/viewer")
def viewer():

    if session.get("user") != "lory":
        return redirect(url_for("login"))

    conn = get_db()

    videos = conn.execute(
        "SELECT * FROM videos ORDER BY id DESC"
    ).fetchall()

    audios = conn.execute(
        "SELECT * FROM audio ORDER BY id DESC"
    ).fetchall()

    photos = conn.execute(
        "SELECT * FROM photos ORDER BY id DESC"
    ).fetchall()

    questions = conn.execute(
        "SELECT * FROM questions ORDER BY id DESC"
    ).fetchall()

    letter = conn.execute(
        "SELECT * FROM letter WHERE id=1"
    ).fetchone()

    conn.close()

    return render_template(
        "viewer.html",
        videos=videos,
        audios=audios,
        photos=photos,
        questions=questions,
        letter=letter
    )


@app.route("/upload_video", methods=["POST"])
def upload_video():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    file = request.files.get("video")
    button_name = request.form.get("button_name")

    if file and file.filename:

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                UPLOAD_VIDEO,
                filename
            )
        )

        conn = get_db()

        conn.execute(
            "INSERT INTO videos(filename,button_name) VALUES(?,?)",
            (
                filename,
                button_name
            )
        )

        conn.commit()
        conn.close()

    return redirect(url_for("admin"))


@app.route("/upload_audio", methods=["POST"])
def upload_audio():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    file = request.files.get("audio")

    if file and file.filename:

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                UPLOAD_AUDIO,
                filename
            )
        )

        conn = get_db()

        conn.execute(
            "INSERT INTO audio(filename) VALUES(?)",
            (filename,)
        )

        conn.commit()
        conn.close()

    return redirect(url_for("admin"))


@app.route("/upload_photo", methods=["POST"])
def upload_photo():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    file = request.files.get("photo")

    if file and file.filename:

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                UPLOAD_PHOTO,
                filename
            )
        )

        conn = get_db()

        conn.execute(
            "INSERT INTO photos(filename) VALUES(?)",
            (filename,)
        )

        conn.commit()
        conn.close()

    return redirect(url_for("admin"))


@app.route("/add_question", methods=["POST"])
def add_question():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO questions(
        question,
        option1,
        option2,
        option3,
        option4
        )
        VALUES(?,?,?,?,?)
        """,
        (
            request.form.get("question"),
            request.form.get("option1"),
            request.form.get("option2"),
            request.form.get("option3"),
            request.form.get("option4")
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route("/save_letter", methods=["POST"])
def save_letter():

    if session.get("user") != "yash":
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        "UPDATE letter SET content=? WHERE id=1",
        (request.form.get("content"),)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
