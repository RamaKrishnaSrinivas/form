import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from dotenv import load_dotenv

# ---------------- Load environment variables ----------------
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- Database connection function ----------------
def connect_to_db():
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("Error: DATABASE_URL environment variable not found.")
        return None

    try:
        conn = psycopg2.connect(database_url)
        print("Database connection successful using raw DATABASE_URL string.")
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

# ---------------- Create users table ----------------
def create_table():
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    mobile INT UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    address VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    feedback VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
        except Exception as e:
            print("Error creating table:", e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

create_table()

# ---------------- Responsive CSS ----------------
base_style = """
<style>
    body {
        font-family: Arial, sans-serif;
        background: #b0aebf;
        margin: 0;
        padding: 0;
    }

    /* ---- Responsive Form Container ---- */
    .form-container {
        width: 90%;
        max-width: 450px;
        margin: 40px auto;
        background: #42b9f5;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
    }

    h1 {
        text-align: center;
        color: #333;
    }

    label {
        display: block;
        margin-top: 10px;
        color: #222;
        font-weight: bold;
    }

    input[type=text],
    input[type=email],
    input[type=tel],
    input[type=date] {
        width: 100%;
        padding: 12px;
        margin-top: 5px;
        border-radius: 8px;
        border: 1px solid #ccc;
        font-size: 16px;
    }

    input[type=submit] {
        width: 100%;
        padding: 12px;
        margin-top: 15px;
        background: #4CAF50;
        color: #fff;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
    }

    input[type=submit]:hover {
        background: #45a049;
    }

    ul { list-style-type: none; padding: 0; }
    li { margin: 5px 0; color: red; text-align: center; }

    /* ---- Mobile View ---- */
    @media (max-width: 480px) {
        .form-container {
            width: 95%;
            padding: 15px;
        }

        input[type=text],
        input[type=email],
        input[type=tel],
        input[type=date],
        input[type=submit] {
            font-size: 15px;
            padding: 10px;
        }
    }
</style>
"""

# ---------------- Templates ----------------
index_template = base_style + """
<div class="form-container">
    <h1>RKSO FORM</h1>
    <form method="POST" action="/">
        <label>NAME</label>
        <input type="text" name="name" required>

        <label>MOBILE</label>
        <input type="tel" name="mobile" required>

        <label>EMAIL</label>
        <input type="email" name="email" required>

        <label>ADDRESS</label>
        <input type="text" name="address" required>

        <label>DOB</label>
        <input type="date" name="dob" required>

        <label>FEEDBACK</label>
        <input type="text" name="feedback" required>

        <input type="submit" value="SUBMIT">
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <ul>
                {% for category, message in messages %}
                    <li>{{ message }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
</div>
"""

# ---------------- Routes ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']
        feedback = request.form['feedback']

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM users WHERE mobile = %s", (mobile,))
                if cur.fetchone():
                    flash("Mobile number already registered!", "red")
                else:
                    cur.execute(
                        "INSERT INTO users (name, mobile, email, address, dob, feedback) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, mobile, email, address, dob, feedback)
                    )
                    conn.commit()
                    flash("Successfully Saved!", "green")
                    return redirect(url_for('index'))
            except psycopg2.Error as e:
                print(f"Database error: {e}") 
                flash("Error saving your data!", "red")
                conn.rollback()
            finally:
                cur.close()
                conn.close()

    return render_template_string(index_template)

# ---------------- Run App ----------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)ort=port)
