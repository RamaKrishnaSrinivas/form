import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from dotenv import load_dotenv

# ---------------- Load environment variables ----------------
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- PostgreSQL settings ----------------
conn = psycopg2.connect(
    dbname="form_wrvb",
    user="form_wrvb_user",
    password="J9BureB3CNSwpmuwDh2ZrpOo8BLs10tq",
    host="dpg-d4mj95be5dus738cq6rg-a.oregon-postgres.render.com",
    port="5432",
    sslmode="require"
)
# ---------------- Database connection ----------------
def connect_to_db():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
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
    app.run(debug=True, host='0.0.0.0', port=5000)
