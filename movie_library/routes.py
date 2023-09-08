import uuid
import functools
from passlib.hash import pbkdf2_sha256
from flask import (
Blueprint, 
render_template,
session,
redirect,
request,
current_app,
url_for,
abort,
flash
)
from forms import MovieForm,ExtendedMovieForm,RegisterForm, LoginForm
from models import Movie, User
from dataclasses import asdict
from datetime import datetime


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper

@pages.route("/")
@login_required
def index():
    movies_all =  current_app.db.movies.find({})
    movies = [(Movie(**movie)) for movie in movies_all]
    return render_template(
        "index.html",
        title="Movies Watchlist",
        movies=movies
    )

@pages.get("/toggle-theme")
def theme():
    current_theme=session.get('theme')
    if current_theme == 'dark':
        session['theme'] = 'light'
    else:
        session['theme'] = 'dark'
    return redirect(request.args.get('current_page'))


@pages.route("/register",methods=["GET","POST"])
def register():
    if session.get("email"):
        return redirect(url_for('.index'))
    
    form=RegisterForm()
    
    if form.validate_on_submit():
        user = User(
        _id = uuid.uuid4().hex,
        email = form.email.data,
        password = form.password.data,
        confirm_password = form.confirm_password.data
        )
        
        current_app.db.users.insert_one(asdict(user))

        flash("User registered successfully", "success")

        return redirect(url_for(".login"))
    
    return render_template('register.html',
                           title="Movies Watchlist - Registration",
                           form=form)

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.users.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and form.password.data == user.password:
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="Movies Watchlist - Login", form=form)



@pages.route("/add_movie",methods=["GET","POST"])
@login_required
def add_movie():
    form = MovieForm()
    
    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
        )
        
        current_app.db.movies.insert_one(asdict(movie))
        return redirect(url_for('pages.index'))

    return render_template('new_movie.html',
                           title="Movies Watchlist",
                           form=form)

@pages.route("/edit/<string:_id>", methods=["GET","POST"])
@login_required
def edit_movie(_id:str):
     movie = Movie(**current_app.db.movies.find_one({"_id":_id}))
     form = ExtendedMovieForm(obj=movie)
     if form.validate_on_submit():
        movie.title = form.title.data
        movie.director = form.director.data
        movie.year = form.year.data
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data

        current_app.db.movies.update_one({"_id":movie._id}, {"$set":asdict(movie)})
        return redirect(url_for(".movie_details",_id=movie._id))    
     
     return render_template('extended_form.html',movie=movie,form=form)   


@pages.get("/movie/<string:_id>")
def movie_details(_id:str):
    movie_data = current_app.db.movies.find_one({"_id":_id})
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data)
    return render_template('movie_details.html',movie=movie)


@pages.get("/movie/<string:_id>/rate")
@login_required
def give_rating(_id):
    rating= int(request.args.get("rating"))
    current_app.db.movies.update_one({"_id":_id}, {"$set":{"rating":rating}})
    return redirect(url_for(".movie_details", _id=_id))


@pages.get("/movie/<string:_id>/watch")
@login_required
def give_date(_id):
     current_app.db.movies.update_one({"_id":_id}, {"$set":{"last_watched":datetime.today()}})
     return redirect(url_for(".movie_details", _id=_id))

@pages.route("/logout")
def log_out():
    session.clear()
    return redirect(url_for('.login'))