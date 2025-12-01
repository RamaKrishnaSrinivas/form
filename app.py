import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- PostgreSQL Settings ----------------
DB_HOST = "dpg-d4mj95be5dus738cq6rg-a.oregon-postgres.render.com"
DB_NAME = "form_wrvb"
DB_USER = "form_wrvb_user"
DB_PASSWORD = "J9BureB3CNSwpmuwDh2ZrpOo8BLs10tq"
DB_PORT = "5432"

# ---------------- DB Connection ----------------
def connect_to_db():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require"
        )
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

# ---------------- Create Table ----------------
def create_table():
    conn = connect_to_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    mobile BIGINT UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    amount INT NOT NULL,
                    date DATE NOT NULL
                )
            """)
            conn.commit()
        except Exception as e:
            print("Error creating table:", e)
        finally:
            conn.close()

create_table()

# ---------------- HTML ----------------
base_style = """
<style>
body { font-family: Arial; background: #b0aebf; }
.container { width: 350px; margin: 50px auto; background: #42b9f5; padding: 20px; border-radius: 8px; }
input, label { width: 100%; margin-top: 10px; }
input[type=submit] { margin-top: 15px; background: #4CAF50; color: white; padding: 10px; border: none; }
ul li { color: red; text-align: center; }
</style>
"""

index_template = base_style + """
<div class="container">
    <h1>Gangamma Trust</h1>
    <form method="POST">
        <label>Name</label>
        <input type="text" name="name" required>
        <label>Mobile</label>
        <input type="tel" name="mobile" required>
        <label>Email</label>
        <input type="email" name="email" required>
        <label>Amount</label>
        <input type="text" name="amount" required>
        <label>Date</label>
        <input type="date" name="date" required>
        <input type="submit" value="SUBMIT">
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
        <ul>
            {% for category, message in messages %}
                <li>{{ message }}</li>
            {% endfor %}
        </ul>
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
        amount = request.form['amount']
        date = request.form['date']

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM users WHERE mobile = %s", (mobile,))
                if cur.fetchone():
                    flash("Mobile already registered!")
                else:
                    cur.execute(
                        "INSERT INTO users (name, mobile, email, amount, date) VALUES (%s, %s, %s, %s, %s)",
                        (name, mobile, email, amount, date)
                    )
                    conn.commit()
                    flash("Successfully Saved!")
                return redirect(url_for("index"))

            except Exception as e:
                flash(str(e))
            finally:
                conn.close()

    return render_template_string(index_template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
