import os
from flask import Flask, render_template, flash, request, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask import Flask, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webform import LoginForm, PostForm, UserForm, PasswordForm, NamerForm
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.secret_key = "BAD_SECRET_KEY" #generet a random secret key


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.config['SECRET_KEY'] = os.urandom(32)

#flask login stuff

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Posts(db.Model):
    # id: Mapped[int] = mapped_column(primary_key=True)
    # poster : Mapped[int] = mapped_column(ForeignKey("users.id"))

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)    
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # foreign key to link User (refer to the primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # poster = relationship('Users', backref='posts')

  


class News(db.Model):
    id = db.Column(db.Integer,primary_key=True)

class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
# password setting
    password_hash = db.Column(db.String(128))
    # posts = relationship('Posts', backref='poster')


    #@property
    #def password(self):
    #     if form.validate_on_submit():
    #      user = Users.query.filter_by(username=form.username.data).first()
    #     if user and user.verify_password(form.password.data):
    #         login_user(user)
    #         return redirect(url_for('index'))
    #     else:
    #         flash('Invalid username or password', 'error')
    # #return render_template('login.html', form=form)

    #         raise AttributeError('password is not a readable!')
    # @password.setter
    # def password(self,password):
    #     self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
        
    def __repr__(self):
        return '<Name %r>' % self.name

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.username)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect if user is already logged in
    
    form = LoginForm()
    
    print(form.errors)
    print(form.validate_on_submit())
    
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user,remember=True)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    # Always return a response, even if the form is not submitted or the login fails
    return render_template('login.html', form=form)

    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#create dashboard page

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    form = UserForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.favorite_color = form.favorite_color.data
        current_user.username = form.username.data
        db.session.commit()
        flash('User updated successfully')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.favorite_color.data = current_user.favorite_color
        form.username.data = current_user.username
    #return render_template('dashboard.html', form=form)




@app.route('/post/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        flash("blog post was delelted")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
    except:
        flash("wooops there was a proble while deleting the blogs, Try Again")



@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted).all()
    return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data


        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated")
        return redirect(url_for('post', id=post.id))
    
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)



#add post page

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, slug=form.slug.data)
        form.title.data=''
        form.content.data=''
        # form.author.data=''
        form.slug.data=''


        db.session.add(post)
        db.session.commit()
        flash("Blog post submitted successfully!")
   

    return render_template("add_post.html", form=form)

   

#jason

@app.route('/date')
def get_current_date():
    return jsonify({"Date": str(date.today())}) 


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")
        return redirect(url_for('add_user'))  # Redirect to a different route after deletion
    except:
        flash("An error occurred while deleting the user", 'error')
        return redirect(url_for('add_user'))  # Redirect to a different route if an error occurs




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
            flash('User updated successfully')
            return redirect(url_for('add_user'))
        except:
            flash('An error occurred while updating the user', 'error')
    return render_template("update.html", form=form, name_to_update=name_to_update)





with app.app_context():
    db.create_all()

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    name = None
    form = UserForm()
   
    print(form.errors)
    print(form.data)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(username= form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            try:
                db.session.commit()
            except Exception as e:
                print(e,'888888')

            
            print(user,'88888')
            name = form.name.data
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''
            flash('User added successfully!')
            return redirect(url_for('add_user'))
        else:
            flash('User with this email already exists!', 'error')
    our_users = Users.query.order_by(Users.date_added).all()
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/')
def hello():
    first_name = 'sarthak'
    stuff = "this is <strong>Bold</strong> Text"
    brand = ["honda", "huyndai", 45]
    return render_template('index.html', first_name=first_name, stuff=stuff, brand=brand)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        pw_to_check = Users.query.filter_by(email=email)

        passed = check_password_hash(pw_to_check.password_hash, password)
   




@app.route('/name', methods=['GET', 'POST'])
def name():
    form = NamerForm()
    if form.validate_on_submit():
        print(form.email.data)
        email = form.email.data
        password = form.password_hash.data
    print(form.email.data,'=============')
    user = Users.query.filter_by(email=form.email.data).first()  # Retrieve the user object
    if user:
        passed = check_password_hash(user.password_hash, password)
    else:
        passed = False  # User does not exist, password check fails
    
    return render_template('name.html', form=form)



if __name__ == "__main__":
    app.run()





