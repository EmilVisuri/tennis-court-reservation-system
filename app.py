from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/tennis_reservation_system'
app.config['SECRET_KEY'] = 'salainen_avain_123'
db = SQLAlchemy(app)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))

class court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_name = db.Column(db.String(50), nullable=False)

class Reservations(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    court_name = db.Column(db.String(50), nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
class time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    times = db.Column(db.String(20), db.ForeignKey('times.id'), nullable=False)
 
with app.app_context():
    db.create_all()
    
@app.route("/make_reservation", methods=["POST"])
def make_reservation():
    # Tarkista, onko käyttäjä kirjautunut sisään
    user_id = session.get('user_id')
    if user_id is None:
        # Ohjaa käyttäjä kirjautumissivulle
        return redirect(url_for("login"))
    
    if "date" in request.form and "time" in request.form and "court_id" in request.form:
        date_str = request.form["date"]
        time_str = request.form["time"]
        court_id = request.form["court_id"]

        # Combine date and time to create a datetime object
        reservation_datetime = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")

        # Retrieve user ID from session
        user_id = session.get('user_id')

        if user_id:
            new_reservation = Reservations(
                customer_id=user_id,
                court_name=court_id,
                date=reservation_datetime.date(),  # Lisätään varauksen päivämäärä
                reservation_time=reservation_datetime.strftime("%H:%M")  # Muunna aika merkkijonoksi
            )

            db.session.add(new_reservation)
            db.session.commit()
            flash("Varaus tehty onnistuneesti!", "success")
            print("User ID:", user_id)
            return redirect(url_for("reservationDone"))

    return redirect(url_for("courts"))

@app.route("/edit_customer_info")
def edit_customer_info():
    user_id = session.get('user_id')
    if user_id:
        customer = Customer.query.get(int(user_id))
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
        customer = Customer.query.get(int(user_id))
        if customer:
            # Päivitä käyttäjän tiedot tietokantaan
            customer.first_name = request.form["first_name"]
            customer.last_name = request.form["last_name"]
            customer.email = request.form["email"]
            customer.phone_number = request.form["phone_number"]
            
            try:
                db.session.commit()
                flash("Tiedot päivitetty onnistuneesti!", "success")
            except Exception as e:
                flash("Virhe päivittäessä tietoja: " + str(e), "error")

            return redirect(url_for("customer_information"))
        else:
            return "Käyttäjää ei löytynyt tietokannasta"
    else:
        return redirect(url_for("login"))
    
@app.route("/delete_reservation")
def delete_reservation():
    # Tarkista, onko käyttäjä kirjautunut sisään
    user_id = session.get('user_id')
    if user_id:
        # Hae käyttäjän varaukset tietokannasta
        customer = Customer.query.get(int(user_id))
        if customer:
            reservations = Reservations.query.filter_by(customer_id=customer.id).all()
            return render_template("delete_reservation.html", reservations=reservations)
        else:
            return "Käyttäjää ei löytynyt tietokannasta"
    else:
        return redirect(url_for("login"))
    
@app.route("/deleted_reservation", methods=["POST"])
def deleted_reservation():
    # Tarkista, onko käyttäjä kirjautunut sisään
    user_id = session.get('user_id')
    if user_id:
        # Hae varauksen ID lomakkeesta
        reservation_id = request.form.get("reservation")
        if reservation_id:
            # Etsi varaus tietokannasta
            reservation = Reservations.query.get(reservation_id)
            if reservation:
                # Poista varaus tietokannasta
                db.session.delete(reservation)
                db.session.commit()
                flash("Varaus poistettu onnistuneesti.", "success")
            else:
                flash("Varausta ei löytynyt.", "error")
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
        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if check_password_hash(customer.password, password):
                session['user_id'] = customer.id
                return redirect(url_for("customer_information"))
            else:
                return redirect(url_for("login"))

    
@app.route("/register", methods=["POST"])
def register():

    if all(key in request.form for key in ["first_name", "last_name", "password", "email", "phone_number"]):
        hashed_password = generate_password_hash(request.form["password"])

        new_customer = Customer(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            password=hashed_password,
            email=request.form["email"],
            phone_number=request.form["phone_number"]
        )
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            return redirect(url_for("front_page"))
        except Exception as e:
            return "Virhe tietokannassa"

@app.route("/")
def front_page():
    return render_template("index.html")

@app.route("/customer_information")
def customer_information():
    user_id = session.get('user_id')
    if user_id:
        customer = Customer.query.get(int(user_id))
        if customer:
            reservations = Reservations.query.filter_by(customer_id=customer.id).all()
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

if __name__ == "__main__":
    app.run(debug=True)