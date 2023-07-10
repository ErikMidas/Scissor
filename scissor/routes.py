from flask import flash, render_template, url_for, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db, cache, limiter, mail, bcrypt
from .models import User, Link
from .forms import LoginForm, RegisterForm
from random import randint
from flask_mail import Message
import random, string, requests, io, qrcode

otp = randint(100000,999999)


def generate_short_link(length=5):
    chars = string.ascii_letters + string.digits
    short_link = "".join(random.choice(chars) for _ in range(length))
    return short_link


def generate_qr_code(link):
    image = qrcode.make(link)
    image_io = io.BytesIO()
    image.save(image_io, "PNG")
    image_io.seek(0)
    return image_io


@app.errorhandler(401)
def unauthorized_page(error):
    return render_template("errors/401.html"), 401


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500


@app.route("/", methods=["GET", "POST"])
@limiter.limit("10/minute")
def home():
    if request.method == "POST":
        long_link = request.form["long_link"]
        custom_link = request.form["custom_link"] or None
        long_link_exists = Link.query.filter_by(user_id=current_user.id).filter_by(long_link=long_link).first()

        if requests.get(long_link).status_code != 200:
            return render_template("errors/404.html")

        elif long_link_exists:
            flash ("This link has already been shortened.")
            return redirect(url_for("dashboard"))

        elif custom_link:
            path_exists = Link.query.filter_by(custom_link=custom_link).first()
            if path_exists:
                flash ("That custom link already exists. Please try another.")
                return redirect(url_for("home"))
            short_link = custom_link

        elif long_link[:4] != "http":
            long_link = "http://" + long_link
        
        else:
            while True:
                short_link = generate_short_link()
                short_link_exists = Link.query.filter_by(short_link=short_link).first()
                if not short_link_exists:
                    break
        
        link = Link(
            long_link=long_link, 
            short_link=short_link, 
            custom_link=custom_link, 
            user_id=current_user.id
        )
        db.session.add(link)
        db.session.commit()
        return redirect(url_for("dashboard"))
    
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dashboard")
@login_required
def dashboard():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).all()
    host = request.host_url
    return render_template("dashboard.html", links=links, host=host)


@app.route("/history")
@login_required
def history():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).all()
    host = request.host_url
    return render_template("history.html", links=links, host=host)


@app.route("/<short_link>")
@cache.cached(timeout=30)
def redirect_link(short_link):
    link = Link.query.filter_by(short_link=short_link).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.long_link)
    else:
        return render_template("errors/404.html")


@app.route("/<short_link>/qr_code")
@login_required
@cache.cached(timeout=30)
@limiter.limit("10/minute")
def generate_qr_code_link(short_link):
    link = Link.query.filter_by(user_id=current_user.id).filter_by(short_link=short_link).first()

    if link:
        image_io = generate_qr_code(request.host_url + link.short_link)
        return image_io.getvalue(), 200, {"Content-Type": "image/png"}
    
    return render_template("errors/404.html")


@app.route("/<short_link>/delete")
@login_required
def delete(short_link):
    link = Link.query.filter_by(user_id=current_user.id).filter_by(short_link=short_link).first()

    if link:
        db.session.delete(link)
        db.session.commit()
        return redirect(url_for("dashboard"))
    
    return render_template("errors/404.html")


@app.route("/<short_link>/edit", methods=["GET", "POST"])
@login_required
@limiter.limit("10/minute")
def update(short_link):
    link = Link.query.filter_by(user_id=current_user.id).filter_by(short_link=short_link).first()
    host = request.host_url
    if link:
        if request.method == "POST":
            custom_link = request.form["custom_link"]
            if custom_link:
                link_exists = Link.query.filter_by(custom_link=custom_link).first()
                if link_exists:
                    flash ("That custom link already exists. Please try another.")
                    return redirect(url_for("update", short_link=short_link))
                link.custom_link = custom_link
                link.short_link = custom_link
            db.session.commit()
            return redirect(url_for("dashboard"))
        return render_template("edit.html", link=link, host=host)
    return render_template("errors/404.html")


@app.route("/<short_link>/analytics")
@login_required
def analytics(short_link):
    link = Link.query.filter_by(user_id=current_user.id).filter_by(short_link=short_link).first()
    host = request.host_url
    if link:
        return render_template("analytics.html", link=link, host=host)
    return render_template("errors/404.html")


@app.route("/signup", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("home"))
    
    form = RegisterForm(request.form)
    
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, username=form.username.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("You have succesfully registered!", "success")

        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "success")
        return redirect(url_for("home"))
    
    form = LoginForm(request.form)
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))