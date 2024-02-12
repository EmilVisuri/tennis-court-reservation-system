from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

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

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
class time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    times = db.Column(db.String(20), db.ForeignKey('times.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/result", methods=["POST"])
def result():
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
            return render_template("user_information.html", user=customer)
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

def get_courts():
    courts = court.query.all()
    return courts

def get_times():
    times = time.query.with_entities(time.times).all()
    return [t[0] for t in times]

@app.route("/courts")
def courts():
    return render_template("courts.html", courts=get_courts(), times=get_times())

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

if __name__ == "__main__":
    app.run(debug=True)