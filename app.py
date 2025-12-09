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
        print("ERROR: DATABASE_URL not set.")
        return None

    try:
        conn = psycopg2.connect(database_url)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print("Database connection error:", e)
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
                    mobile VARCHAR(20) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    address VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    feedback VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()
            print("Table 'users' created or already exists.")
        except Exception as e:
            print("Error creating table:", e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

create_table()

# ---------------- Basic CSS (UPDATED FOR RESPONSIVENESS) ----------------
base_template = """
<style>
/* --- Basic Reset & Setup --- */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    background-color: lightgray;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
}

/* --- Container Styling --- */
.container {
    background-color: lightblue;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 500px; /* Limits the form width on large screens */
}

h1 {
    text-align: center;
    color: #333;
    border-bottom: 2px solid #007bff;
}

/* --- Form Element Styling --- */
form {
    display: flex;
    flex-direction: column;
}

label {
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
    display: block;
}

/* Style for all input types in the form */
input[type="text"],
input[type="tel"],
input[type="email"],
input[type="date"] {
    width: 100%;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
    transition: border-color 0.3s;
}

input:focus {
    border-color: green;
    outline: none;
}

/* Specific styling for the submit button */
input[type="submit"] {
    background-color: #007bff;
    color: white;
    padding: 14px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 18px;
    transition: background-color 0.3s;
}

input[type="submit"]:hover {
    background-color: #0056b3;
}

ul {
    list-style-type: none;
    padding: 0;
}

li {
    margin: 5px 0;
    color: red;
    text-align: center;
}
</style>
"""
# ---------------- Templates ----------------
index_template =base_template + """
<div class="container">
<h1>RKSO FORM</h1><br />
<form method="POST" action="/">
<label>NAME</label>
<input type="text" name="name" required>
<br />
<label>MOBILE</label>
<input type="tel" name="mobile" required>
<br />
<label>EMAIL</label>
<input type="email" name="email" required>
<br />
<label>ADDRESS</label>
<input type="text" name="address" required>
<br />
<label>DOB</label>
<input type="date" name="dob" required>
<br />
<label>FEEDBACK</label>
<input type="text" name="feedback" required>
<br /><br />
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
        mobile = request.form['mobile']  # keep as TEXT, do NOT convert to int
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']
        feedback = request.form['feedback']

        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            try:
                # check if mobile already exists
                cur.execute("SELECT id FROM users WHERE mobile = %s", (mobile,))
                if cur.fetchone():
                    flash("Mobile number already registered!", "red")
                else:
                    cur.execute("""
                        INSERT INTO users (name, mobile, email, address, dob, feedback)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (name, mobile, email, address, dob, feedback))
                    conn.commit()
                    flash("Successfully Saved!", "green")
                    return redirect(url_for('index'))
            except Exception as e:
                print("Database insert error:", e)
                flash("Error saving data. Please check your entries.", "red")
                conn.rollback()
            finally:
                cur.close()
                conn.close()

    return render_template_string(index_template)

# ---------------- Run App ----------------
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
