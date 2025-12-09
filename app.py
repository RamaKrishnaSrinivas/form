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
base_style = """
<style>
/* Basic Reset and Body Styling */
body {
    font-family: Arial, sans-serif;
    background: #b0aebf;
    margin: 0;
    padding: 0;
    box-sizing: border-box; /* Ensures padding/border are included in element's total width */
}

/* Responsive Container */
.container {
    width: 90%; /* Use percentage for flexibility */
    max-width: 400px; /* Prevents it from getting too wide on large screens */
    margin: 50px auto; /* Centers the container */
    background: #42b9f5;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 20px black;
}

h1 {
    text-align: center;
    color: #333;
}

label {
    display: block;
    margin-top: 10px;
    color: #555;
}

/* Ensure all input fields are responsive */
input[type=text],
input[type=email],
input[type=tel],
input[type=date] {
    width: 100%; /* Takes full width of its parent (minus padding/border due to box-sizing) */
    padding: 10px; /* Increased padding for better mobile usability */
    margin-top: 5px;
    border-radius: 4px;
    border: 1px solid #ccc;
    box-sizing: border-box; /* Crucial for width: 100% to work correctly with padding */
}

input[type=submit] {
    width: 100%;
    padding: 10px;
    margin-top: 15px;
    background: #4CAF50;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    box-sizing: border-box;
}

input[type=submit]:hover {
    background: #45a049;
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

/* Media Query for very small screens (e.g., older phones) if needed, though not strictly necessary with the above changes */
/*
@media (max-width: 600px) {
    .container {
        width: 95%;
        margin: 20px auto;
    }
}
*/

</style>
"""

# ---------------- Templates ----------------
index_template = base_style + """
<div class="container">
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
