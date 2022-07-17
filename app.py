import email
from email.policy import default
from turtle import title
from flask import Flask, current_app, redirect, render_template, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NameForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


#Create a Flask istance
app = Flask(__name__)
#Add CKEditor 
ckeditor = CKEditor(app)
#Add Database
# Old SQLite DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Lytvynyuk87@localhost/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vjqaobumwyqgbb:443f87e234a28b8ae7dc2bde75ac018578979cdb171c4c9aefa17c0a42dcd481@ec2-52-205-61-230.compute-1.amazonaws.com:5432/de1vl0h9dptjrc'
# Secret Key
app.config['SECRET_KEY'] = 'secret123'
#Upload folder for profile pics
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Pass Staff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)   

#Create admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id ==17:
        return render_template("admin.html")
    else:
        flash("Sorry you must be Administrator to login on this page!")
        return redirect(url_for('dashboard'))


#Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #Get data from submitted form
        post.searched = form.searched.data
        #Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html", form=form, searched=post.searched, posts=posts)


#Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesful!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password, Try Again!")
        else:
            flash("That User Doesn't exist!")
    return render_template('login.html', form=form)

#Create Logout page(function)
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Are Logged Out!")
    return redirect(url_for('login'))

#Create Dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']        
        #Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        #Set UUID
        pic_modified_name = str(uuid.uuid1()) + "_" + pic_filename
        #Save that image (which is up on code)
        saver = request.files['profile_pic']
        #Take a filename to save it in database
        name_to_update.profile_pic = pic_modified_name
        try:
            db.session.commit()            
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_modified_name)
            flash("User Updated Successfully!")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            flash("Error! Some problem!")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    return render_template('dashboard.html')


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            #return a message
            flash("Post was deleted!")

            #Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            #Return an error message
            flash("There was a problem deleting post!")

           #Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        #return a message
        flash("You are not authorized to delete this post!")
            
        #Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

@app.route('/posts')
#@login_required
def posts():
    #Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
#@login_required
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        
        #Update data in Database
        db.session.add(post)
        db.session.commit()

        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You are not authorized to edit this post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

#Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
#@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        form.title.data = '' #Clear content of form after submit
        form.content.data = ''
        #form.author.data = '' не потрібно бо прив'язали користувача до поста в базі даних
        form.slug.data = ''

        #Add post data to database
        db.session.add(post)
        db.session.commit()

        #Return a Message
        flash("Blog Post Submitted Successfully!")
    
    #Redirect to the webpage
    return render_template("add_post.html", form=form)

#JSON Thing
@app.route('/date')
def qet_current_date():
    favorite_pizza = {
        "John": "Pepperoni",
        "Mary": "Cheese",
        "Tim": "mashroom"
    }
    return favorite_pizza

    #return {"Date": date.today()}


@property
def password(self):
    raise AttributeError('password is not a readable attribute')

@password.setter
def password(self, password):
    self.password_hash = generate_password_hash(password)

def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

 #Create A String
def __repr__(self):
    return '<Name %r>' % self.name



#Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error! Some problem!")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

#Create a route decorator
@app.route('/')
def index():
    first_name = "Yaroslaw"
    return render_template("index.html", first_name=first_name)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username = form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''

        flash("User Added Successfuly!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)
    
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("Something went wrong!") 
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

#def index():
#    return "<h1>Hello world</h1>"

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name = name)


#Create custom Error pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


#Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()

   #  Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted succesfully")

    return render_template('name.html', name = name, form = form)

#Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    #  Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        #Lookup User by Email address
        pw_to_check = Users.query.filter_by(email=email).first()

        #Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

        #flash("Form Submitted succesfully")

    return render_template('test_pw.html', email = email, password=password, pw_to_check=pw_to_check, passed=passed, form = form)


#Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(128), nullable=True)
    # Do some password staff!
    password_hash = db.Column(db.String(128))
    #User Can Have Many Posts
    posts = db.relationship('Posts', backref='poster')
    

if __name__ == "__main__":
    app.run(debug=True)  
