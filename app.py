from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "stress_secret"

def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT)
    """)
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        conn.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                     (name, email, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)).fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", name=session["user"])

@app.route("/predict", methods=["POST"])
def predict():
    answers = [int(request.form[f"q{i}"]) for i in range(1, 11)]
    score = sum(answers)

    if score <= 15:
        level = "Low Stress"
        tips = [
            "Maintain healthy sleep schedule",
            "Continue hobbies you enjoy",
            "Stay socially active"
        ]
    elif score <= 25:
        level = "Medium Stress"
        tips = [
            "Practice meditation or breathing exercises",
            "Improve time management",
            "Take breaks during work/study"
        ]
    else:
        level = "High Stress"
        tips = [
            "Consider speaking to a therapist",
            "Reduce workload temporarily",
            "Spend time with supportive people",
            "Practice mindfulness daily"
        ]

    return render_template("result.html", level=level, score=score, tips=tips)

if __name__ == "__main__":
    app.run(debug=True)
