from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'salainen_avain_123'
csrf = CSRFProtect(app)

def db_connection():
    return psycopg2.connect(
        host="localhost",
        database="tennis_reservation_system",
        user="postgres",
        password="your_password"
    )

@app.route("/make_reservation", methods=["POST"])
def make_reservation():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for("login"))
    
    if "date" in request.form and "time" in request.form and "court_id" in request.form:
        date_str = request.form["date"]
        time_str = request.form["time"]
        court_id = request.form["court_id"]
        reservation_datetime = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
        user_id = session.get('user_id')

        if user_id:
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO reservations (customer_id, court_name, date, reservation_time) VALUES (%s, %s, %s, %s)",
                        (user_id, court_id, reservation_datetime.date(), reservation_datetime.strftime("%H:%M")))
            conn.commit()
            cur.close()
            conn.close()

            flash("Varaus tehty onnistuneesti!", "success")
            return redirect(url_for("reservationDone"))

    return redirect(url_for("courts"))

@app.route("/edit_customer_info")
def edit_customer_info():
    user_id = session.get('user_id')
    if user_id:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE id = %s", (user_id,))
        customer = cur.fetchone()
        cur.close()
        conn.close()

        if customer:
            return render_template("edit.html", user=customer)
        else:
            return "Käyttäjää ei löytynyt tietokannasta"
    else:
        return redirect(url_for("login"))
    
@app.route("/update_customer_info", methods=["POST"])
def update_customer_info():
    user_id = session.get('user_id')
    if user_id:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET first_name=%s, last_name=%s, email=%s, phone_number=%s WHERE id=%s",
                    (request.form["first_name"], request.form["last_name"], request.form["email"], request.form["phone_number"], user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Tiedot päivitetty onnistuneesti!", "success")
        return redirect(url_for("customer_information"))
    else:
        return redirect(url_for("login"))
    
@app.route("/delete_reservation")
def delete_reservation():
    user_id = session.get('user_id')
    if user_id:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM reservations WHERE customer_id = %s", (user_id,))
        reservations = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("delete_reservation.html", reservations=reservations)
    else:
        return redirect(url_for("login"))
    
@app.route("/deleted_reservation", methods=["POST"])
def deleted_reservation():
    user_id = session.get('user_id')
    if user_id:
        reservation_id = request.form.get("reservation")
        if reservation_id:
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM reservations WHERE id = %s AND customer_id = %s", (reservation_id, user_id))
            conn.commit()
            cur.close()
            conn.close()
            flash("Varaus poistettu onnistuneesti.", "success")
        else:
            flash("Valitse varaus poistettavaksi.", "error")
        return redirect(url_for("customer_information"))
    else:
        return redirect(url_for("login"))

@app.route("/result", methods=["POST"])
def result():
    if 'user_id' in session:
        return redirect(url_for("customer_information"))

    if all(key in request.form for key in ["email", "password"]):
        email = request.form["email"]
        password = request.form["password"]
        
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM customers WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            customer_id, hashed_password = result
            if check_password_hash(hashed_password, password):
                session['user_id'] = customer_id
                return redirect(url_for("customer_information"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))

@app.route("/register", methods=["POST"])
def register():

    if all(key in request.form for key in ["first_name", "last_name", "password", "email", "phone_number"]):
        hashed_password = generate_password_hash(request.form["password"])

        conn = db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO customers (first_name, last_name, password, email, phone_number) VALUES (%s, %s, %s, %s, %s)",
                    (request.form["first_name"], request.form["last_name"], hashed_password, request.form["email"], request.form["phone_number"]))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("front_page"))
    else:
        return "Virhe tietokannassa"

@app.route("/")
def front_page():
    return render_template("index.html")

@app.route("/customer_information")
def customer_information():
    user_id = session.get('user_id')
    if user_id:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE id = %s", (user_id,))
        customer = cur.fetchone()
        cur.execute("SELECT * FROM reservations WHERE customer_id = %s", (user_id,))
        reservations = cur.fetchall()
        cur.close()
        conn.close()

        if customer:
            return render_template("user_information.html", user=customer, reservations=reservations)
        else:
            return "Käyttäjää ei löytynyt tietokannasta"
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for("front_page"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/courts")
def courts():
    return render_template("courts.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

@app.route('/reservationDone')
def reservationDone():
    return render_template('reservationDone.html')