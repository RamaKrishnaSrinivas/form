import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
# Import dj_database_url for parsing the URL and handling SSL
import dj_database_url 
from dotenv import load_dotenv

# ---------------- Load environment variables ----------------
# For local development, this loads variables from a local .env file.
# On Render, the variables are provided by the environment automatically.
load_dotenv()

app = Flask(__name__)
# Fetch the SECRET_KEY from environment variables for security.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- Database connection function ----------------
def connect_to_db():
    # Retrieve the full database URL from environment variables
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL environment variable not found.")
        return None

    conn = None
    try:
        # 1. Parse the URL using dj_database_url
        conn_params = dj_database_url.parse(database_url)
        
        # 2. CRITICAL FIX: Convert all dictionary keys to lowercase (e.g., 'USER' -> 'user')
        #    and remove the 'ENGINE' key which is Django-specific and causes psycopg2 to error.
        cleaned_params = {k.lower(): v for k, v in conn_params.items()}

        if 'engine' in cleaned_params:
            del cleaned_params['engine'] 

        # 3. Connect using the cleaned parameters
        conn = psycopg2.connect(**cleaned_params)
        print("Database connection successful using DATABASE_URL.")
        return conn
    except Exception as e:
        print(f"Error connecting via DATABASE_URL: {e}")
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
            conn.rollback() # Rollback on error
        finally:
            cur.close()
            conn.close()

# Ensure the table is created when the app starts
create_table()

# ---------------- Basic CSS (Remains the same) ----------------
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

# ---------------- Templates (Remains the same) ----------------
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

# ---------------- Routes (Remains the same) ----------------
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
                print(f"Database error during insertion: {e}") 
                flash("An error occurred while saving your data. Please check your inputs.", "red")
                conn.rollback()
            finally:
                cur.close()
                conn.close()

    return render_template_string(index_template)

# ---------------- Run App ----------------
if __name__ == '__main__':
    # Use the PORT provided by the environment (Render), default to 5000 for local dev
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
