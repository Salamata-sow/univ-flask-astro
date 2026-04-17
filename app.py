from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- CONFIG DB ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/astro_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))


class Appareil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100))
    modele = db.Column(db.String(100))
    date_sortie = db.Column(db.String(50))
    score = db.Column(db.Integer)
    categorie = db.Column(db.String(50))


class Telescope(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100))
    modele = db.Column(db.String(100))
    date_sortie = db.Column(db.String(50))
    score = db.Column(db.Integer)
    categorie = db.Column(db.String(50))


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100))
    image_url = db.Column(db.String(300))
    categorie = db.Column(db.String(50))
    auteur = db.Column(db.String(100))
    date_photo = db.Column(db.String(50))


# ---------------- INIT DB + SEED ----------------
with app.app_context():
    db.create_all()

    # ---- Appareils ----
    if Appareil.query.count() == 0:
        db.session.add_all([
            Appareil(
                marque="Canon",
                modele="EOS 90D",
                date_sortie="2019",
                score=5,
                categorie="Amateur"
            ),
            Appareil(
                marque="Nikon",
                modele="D7500",
                date_sortie="2017",
                score=4,
                categorie="Amateur sérieux"
            ),
            Appareil(
                marque="Sony",
                modele="A7 IV",
                date_sortie="2021",
                score=5,
                categorie="Professionnel"
            ),
        ])
        db.session.commit()

    # ---- TELESCOPES ----
    if Telescope.query.count() == 0:
        db.session.add_all([
            Telescope(
                marque="Celestron",
                modele="AstroMaster 70AZ",
                date_sortie="2020",
                score=4,
                categorie="Enfant"
            ),
            Telescope(
                marque="Sky-Watcher",
                modele="Star Discovery",
                date_sortie="2018",
                score=5,
                categorie="Automatisé"
            ),
            Telescope(
                marque="Orion",
                modele="SkyQuest XT8",
                date_sortie="2016",
                score=5,
                categorie="Complet"
            ),
        ])
        db.session.commit()

    # ---- PHOTOS ----
    if Photo.query.count() == 0:
        db.session.add_all([
            Photo(
                titre="Nébuleuse",
                image_url="https://upload.wikimedia.org/wikipedia/commons/f/f3/Orion_Nebula_-_Hubble_2006_mosaic_18000.jpg",
                categorie="Nebuleuse",
                auteur="NASA",
                date_photo="2023-05-12"
            ),
            Photo(
                titre="Galaxie spirale",
                image_url="https://via.placeholder.com/400x250",
                categorie="Galaxie",
                auteur="Hubble",
                date_photo="2022-11-03"
            ),
            Photo(
                titre="Lune",
                image_url="https://via.placeholder.com/400x250",
                categorie="Lune",
                auteur="ESA",
                date_photo="2024-01-18"
            ),
        ])
        db.session.commit()


# ---------------- AUTH ----------------

def is_logged():
    return "user" in session


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    if not is_logged():
        return redirect("/login")
    return render_template("base.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            error = "Utilisateur déjà existant"
        else:
            db.session.add(User(
                username=username,
                password=generate_password_hash(password)
            ))
            db.session.commit()
            return redirect("/login")

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.username
            return redirect("/")
        else:
            error = "Mauvais identifiants"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- PAGES ----------------

@app.route("/appareils")
def appareils():
    if not is_logged():
        return redirect("/login")
    return render_template("appareils.html", appareils=Appareil.query.all())


@app.route("/telescopes")
def telescopes():
    if not is_logged():
        return redirect("/login")
    return render_template("telescopes.html", telescopes=Telescope.query.all())


@app.route("/photos")
def photos():
    if not is_logged():
        return redirect("/login")
    return render_template("photos.html", photos=Photo.query.all())


# ---------------- DEBUG ----------------

@app.route("/debug-appareils")
def debug_appareils():
    return str([(a.marque, a.categorie) for a in Appareil.query.all()])


@app.route("/debug-photos")
def debug_photos():
    return str([(p.titre, p.image_url) for p in Photo.query.all()])


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)