from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # USERS TABLE
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    ''')

    # SAVED QUESTIONS TABLE
    cur.execute('''
    CREATE TABLE IF NOT EXISTS saved_questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------

@app.route("/")
def home():
    return render_template("index.html")

# ---------- REGISTER ----------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                    (name,email,password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------- LOGIN ----------

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                    (email,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------- DASHBOARD ----------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE id=?", (user_id,))
    score = cursor.fetchone()[0]
    conn.close()

    return render_template("dashboard.html", score=score)
# ---------- APTITUDE ----------

import random

@app.route("/aptitude")
def aptitude():
    if "user_id" not in session:
        return redirect("/login")

    questions = [
        "A train 150 meters long is moving at 45 km/hr. How long will it take to cross a pole?",
        "Find the simple interest on Rs.5000 at 10% per annum for 2 years.",
        "The ratio of boys to girls in a class is 3:2. If there are 30 boys, how many girls are there?",
        "A man walks 10 km in 2 hours. What is his speed?",
        "If the cost price is 200 and selling price is 240, find the profit percentage."
    ]

    q = random.choice(questions)

    return render_template("aptitude.html", question=q)

# ---------- CODING ----------

@app.route("/coding")
def coding():
    if "user_id" not in session:
        return redirect("/login")

    import random

    coding_questions = [
        ("Check Palindrome Number",
         "Write a program to check whether a number is palindrome or not.",
         "Logic: Reverse the number using loop and compare with original."),

        ("Find Largest Element",
         "Write a program to find largest number in an array.",
         "Logic: Traverse array and keep track of max value."),

        ("Prime Number",
         "Check whether a number is prime or not.",
         "Logic: Check divisibility from 2 to sqrt(n)."),

        ("Fibonacci Series",
         "Print first N Fibonacci numbers.",
         "Logic: Use two variables and loop."),

        ("Factorial",
         "Find factorial of a number.",
         "Logic: Use loop from 1 to n and multiply.")
    ]

    title, question, logic = random.choice(coding_questions)

    return render_template("coding.html",
                           title=title,
                           question=question,
                           logic=logic)

# ---------- HR ----------

import random

@app.route("/hr")
def hr():
    if "user_id" not in session:
        return redirect("/login")

    hr_questions = [
        ("Tell me about yourself.",
         "I am a motivated engineering student with strong problem solving and programming skills. I enjoy learning new technologies and applying them in real world projects."),

        ("Why should we hire you?",
         "I am a quick learner, hardworking and adaptable. I can contribute to the team and continuously improve my skills while helping the company grow."),

        ("What are your strengths?",
         "My strengths are logical thinking, patience, and the ability to learn new concepts quickly."),

        ("What is your weakness?",
         "I sometimes focus too much on details, but I am learning to manage time efficiently."),

        ("Where do you see yourself in 5 years?",
         "I see myself as a skilled software engineer working on real world applications and taking more responsibilities.")
    ]

    q, ans = random.choice(hr_questions)

    return render_template("hr.html", question=q, answer=ans)

# ---------- SAVE QUESTION ----------

@app.route("/save_question", methods=["POST"])
def save_question():
    if "user_id" not in session:
        return redirect("/login")

    question = request.form["question"]
    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # store question
    cursor.execute(
        "INSERT INTO saved_questions(user_id,question) VALUES(?,?)",
        (user_id, question)
    )

    # update score
    cursor.execute(
        "UPDATE users SET score = score + 1 WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/aptitude?saved=1")

# ---------- VIEW SAVED QUESTIONS ----------

@app.route("/saved")
def saved():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT question FROM saved_questions WHERE user_id=?", (user_id,))
    questions = cur.fetchall()
    conn.close()

    return render_template("saved.html", questions=questions)

    # ---------- PRACTICE QUESTIONS ----------
@app.route('/practice', methods=['GET','POST'])
def practice():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == 'POST':
        question = request.form.get("question")
        user_id = session["user_id"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO saved_questions(user_id,question) VALUES(?,?)",
                       (user_id, question))

        conn.commit()
        conn.close()

        return "Question Saved Successfully!"

    return render_template('practice.html')

# ---------- LOGOUT ----------

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
