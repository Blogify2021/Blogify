import os
from flask import Flask, render_template, redirect, url_for, abort
from flask.globals import request
import datetime as dt
# from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
# from functools import wraps
from send_mail import SendMail
#from dotenv import load_dotenv
# load_dotenv(".env")
app = Flask(__name__)
#app.config['SECRET_KEY'] = os.getenv('APP_SECRET')
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET')
ckeditor = CKEditor(app)
# Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",  "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# CONFIGURE TABLES


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(50), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text, nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    username = db.Column(db.String(20))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    user = relationship("UserProfile", back_populates="user")
    is_admin = db.Column(db.Boolean)


class UserProfile(db.Model):
    __tablename__ = "user_profile"
    id = db.Column(db.Integer, primary_key=True)
    dob = db.Column(db.String(100))
    quote = db.Column(db.String(100))
    img_url = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="user")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="comments")

    date_time = db.Column(db.String(100))

    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    parent_post = relationship("BlogPost", back_populates="comments")


db.create_all()


# def adminsToDel(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         post = BlogPost.query.get(args)
#         if (current_user == post.author) or (current_user.is_admin):
#             return f(*args, **kwargs)
#         return abort(403)
#     return decorated_function


# def adminsToEdit(argument):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             post = BlogPost.query.get(argument)
#             if (current_user == post.author):
#                 return function(*args, **kwargs)
#             return abort(403)
#         return wrapper
#     return decorator


# def adminsToEdit(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         post = BlogPost.query.get(args)
#         if (current_user == post.author):
#             return f(*args, **kwargs)
#         return abort(403)
#     return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()[::-1]
    return render_template("Index.html", all_posts=posts, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form.to_dict()
        if User.query.filter_by(email=form["email"]).first():
            return redirect(url_for('login', class_="warn", message="this email is already registered"))
        new_user = User(
            username=form["username"],
            email=form["email"],
            password=generate_password_hash(form["password"]),
            is_admin=False
            # is_admin=True
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("new_profile"))
    return render_template("signup.html", logged_in=current_user.is_authenticated)


@app.route('/login/<class_>/<message>', methods=["GET", "POST"])
def login(class_, message):

    if request.method == "POST":
        form = request.form.to_dict()
        email = form["email"]
        password = form["password"]
        account = User.query.filter_by(email=email).first()
        if not account:
            message = "Email do not exist"
            class_ = "warn"
        elif not check_password_hash(account.password, password):
            message = "Password is incorrect,try again"
            class_ = "error"
        else:
            login_user(account)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", logged_in=current_user.is_authenticated, class_=class_, message=message)


@app.route('/newprofile', methods=["GET", "POST"])
@login_required
def new_profile():
    if request.method == "POST":
        form = request.form.to_dict()
        new_profile = UserProfile(
            dob=form["dob"],
            quote=form["quote"],
            img_url=form["img_url"],
            about=form["about"],
            user=current_user
        )
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    user_details = {
        "dob": "",
        "quote": "",
        "image_url": "",
        "about": "Write something about you......"
    }
    return render_template("edit.html", access_point="new user", current_user=current_user, user_details=user_details)


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user_id = current_user.id
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if user_profile.img_url == "../static/Assets/Images/UserBG.jpg":
        user_profile.img_url = ""
        db.session.commit()
    if request.method == "POST":
        edit_form = request.form.to_dict()
        user_profile.dob = edit_form["dob"]
        user_profile.quote = edit_form["quote"]
        user_profile.img_url = edit_form["img_url"]
        user_profile.about = edit_form["about"]
        db.session.commit()
        return redirect(url_for("show_user_profile", user_id=user_id))

    return render_template("edit.html", access_point="edit profile", current_user=current_user, user_details=user_profile)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/user/<int:user_id>")
def show_user_profile(user_id):
    all_posts = BlogPost.query.all()
    author = User.query.get(user_id)
    user_posts = []
    for post in all_posts:
        if post.user_id == user_id:
            user_posts.append(post)
    try:
        author.user[0].img_url
    except IndexError:
        new_profile = UserProfile(
            dob="",
            quote="",
            img_url="../static/Assets/Images/UserBG.jpg",
            about="",
            user=author
        )
        db.session.add(new_profile)
        db.session.commit()

    return render_template("user.html", posts=user_posts, count=0, card_value="", author=author, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):

    requested_post = BlogPost.query.get(post_id)
    if request.method == "POST":
        form = request.form.to_dict()
        if not current_user.is_authenticated:
            return redirect(url_for('login', class_="warn", message="you need to login to write comment"))
        else:
            date_time = dt.datetime.now().strftime('%y-%m-%d %a %H:%M')
            new_comment = Comment(
                text=form["comment"],
                author=current_user,
                parent_post=requested_post,
                date_time=date_time
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(request.referrer)
    return render_template("post.html", post=requested_post, logged_in=current_user.is_authenticated, current_user=current_user)


@app.route("/deletecomment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if (current_user == comment.author) or (current_user.is_admin):
        db.session.delete(comment)
        db.session.commit()
        return redirect(request.referrer)
    return abort(403)

# @app.route("/about")
# def about():
#     return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        form = request.form.to_dict()
        SendMail(form)
        return redirect(url_for('get_all_posts'))
    return render_template("contactus.html", logged_in=current_user.is_authenticated)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    if request.method == "POST":
        form = request.form.to_dict()
        new_post = BlogPost(
            title=form["title"],
            subtitle=form["subtitle"],
            body=form["body"],
            img_url=form["img_url"],
            author=current_user,
            date=dt.date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    post = {"title": "",
            "subtitle": "",
            "img_url": "",
            "body": "write blog here......."}
    return render_template("edit.html", access_point="new blog", current_user=current_user, post=post)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    if (current_user == post.author):
        if request.method == "POST":
            edit_form = request.form.to_dict()
            post.title = edit_form["title"]
            post.subtitle = edit_form["subtitle"]
            post.img_url = edit_form["img_url"]
            post.body = edit_form["body"]
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))

        return render_template("edit.html", access_point="edit post", logged_in=current_user.is_authenticated, post=post)
    return abort(403)


@app.route("/deletepost/<int:post_id>")
@login_required
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    if (current_user == post.author) or (current_user.is_admin):
        comments = Comment.query.filter_by(post_id=post_id)
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return abort(403)


@app.route("/deleteaccount/<int:user_id>")
@login_required
def delete_account(user_id):
    user = User.query.get(user_id)
    if (current_user == user) or (current_user.is_admin):
        comments = Comment.query.filter_by(user_id=user_id)
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
        posts = BlogPost.query.filter_by(user_id=user_id)
        for post in posts:
            post_id = post.id
            comments = Comment.query.filter_by(post_id=post_id)
            for comment in comments:
                db.session.delete(comment)
                db.session.commit()
            post_to_delete = BlogPost.query.get(post_id)
            db.session.delete(post_to_delete)
            db.session.commit()
        userprofile = UserProfile.query.filter_by(user_id=user_id)[0]
        db.session.delete(userprofile)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return abort(403)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
