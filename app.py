import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from dotenv import load_dotenv
import dj_database_url

# ---------------- Load environment variables ----------------
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- PostgreSQL settings ----------------
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME', 'notepad_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'skro@0513')
DB_PORT = os.getenv('DB_PORT', 5432)

# ---------------- Database connection ----------------
def connect_to_db():
    # Try connecting using the standard DATABASE_URL environment variable first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            # dj_database_url parses the URL into psycopg2 arguments
            conn_params = dj_database_url.parse(database_url)
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"Error connecting via DATABASE_URL: {e}")
            return None
    
    # Fallback to individual variables if DATABASE_URL is not set (useful for local testing)
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode='DB_SSLMODE'
        )
    except psycopg2.Error as e:
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
                    mobile BIGINT UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    amount INT NOT NULL,
                    date DATE NOT NULL
                )
            """)
            conn.commit()
            print("Table 'users' created or already exists.")
        except Exception as e:
            print("Error creating table:", e)
        finally:
            conn.close()

create_table()

# ---------------- Basic CSS ----------------
base_style = """
    <style>
        body { font-family: Arial, sans-serif; background: #b0aebf; margin:0; padding:0; }
        .container { width: 350px; margin: 50px auto; background: #42b9f5; padding: 20px; border-radius: 8px; box-shadow: 0 0 20px; border-color: black;  }
        h1 { text-align: center; color: #333; }
        label { display: block; margin-top: 10px; color: #555; }
        input[type=text], input[type=email], input[type=tel], input[type=date], input[type=amount] {
            width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ccc;
        }
        input[type=submit] { width: 100%; padding: 10px; margin-top: 15px; background: #4CAF50; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        input[type=submit]:hover { background: #45a049; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 5px 0; color: red; text-align: center; }
        a { color: #4CAF50; text-decoration: none; }
        a:hover { text-decoration: underline; }
        nav ul { text-align: center; }
        nav ul li { display: inline; margin: 0 10px; }
    </style>
"""

# ---------------- Templates ----------------
index_template = base_style + """
    <div class="container">
        <h1>Welcome to Gangamma Trust</h1>
        <form method="POST" action="/">
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
        amount = request.form['amount']
        date = request.form['date']

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                # Check if mobile already exists
                cur.execute("SELECT id FROM users WHERE mobile = %s", (mobile,))
                if cur.fetchone():
                    flash("Mobile number already registered!", "red")
                else:
                    cur.execute(
                        "INSERT INTO users (name, mobile, email, amount, date) VALUES (%s, %s, %s, %s, %s)",
                        (name, mobile, email, amount, date)
                    )
                    conn.commit()
                    flash("Successfully Saved!", "green")
                    return redirect(url_for('index'))
            except psycopg2.Error as e:
                flash(f"Invalid data or DB error: {e}", "red")
            finally:
                conn.close()

    return render_template_string(index_template)

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
