import os
from flask import Flask, render_template, flash, request, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask import Flask, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webform import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey
from flask_ckeditor import CKEditor 
from  werkzeug.utils import secure_filename
import uuid as uuid



app = Flask(__name__)
ckeditor = CKEditor(app)
app.secret_key = "BAD_SECRET_KEY" #generet a random secret key


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.config['SECRET_KEY'] = os.urandom(32)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#flask login stuff

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)
#create admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash("sorry you are not the admin")
        return redirect(url_for('dashboard'))


#create Search Function
@app.route('/search', methods=["POST"])

def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data

        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()


        return render_template("search.html", form=form, searched = post.searched, posts = posts)
    return render_template("search.html", form=form)
class Posts(db.Model):
    #id: Mapped[int] = mapped_column(primary_key=True)
    #poster : Mapped[int] = mapped_column(ForeignKey("users.id"))
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)    
   #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # foreign key to link User (refer to the primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    poster = relationship('Users', backref='poster', cascade='all')
    #poster = relationship('Users', backref='Posts', cascade='all, delete-orphan')


    # Foreign key to link user (refer to the primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


  


class News(db.Model):
    id = db.Column(db.Integer,primary_key=True)

class Users(db.Model,UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)

    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)

    # Define the relationship with Posts
    user_posts = relationship('Posts', backref='user', cascade='all')
    # password setting
    password_hash = db.Column(db.String(128))


    @property
    def password(self):
        if form.validate_on_submit():
          user = Users.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
             flash('Invalid username or password', 'error')
        return render_template('login.html', form=form)

        raise AttributeError('password is not a readable!')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

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
    
    
    
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user,remember=True)
            print('hey')
            return redirect(url_for('add_post'))
        else:
            flash('Invalid username or password', 'error')
    
    # Always return a response, even if the form is not submitted or the login fails
    return render_template('login.html', form=form)

    
@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))


#create dashboard page

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    form = UserForm()
    print(form.errors,'&&&&&&&')
    print(request.method)
    if current_user.is_authenticated and request.method == "GET":
        # return render_template('dashboard.html', form=form)
        # return render_template('test.html')
        return render_template('dashboard.html', form=form)

    print(form.validate_on_submit())
    # print(form.form_errors)
    if request.method =="POST":
        print(form.about_author,'*******')        
        print(form.profile_pic,'*****')        
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.favorite_color = form.favorite_color.data
        current_user.username = form.username.data
        current_user.about_author = form.about_author.data
        
        #check for profile pic
        if form.profile_pic.data:
            current_user.profile_pic = form.profile_pic.data


        
            #grab image name
            pic_filename = secure_filename(form.profile_pic.data.filename)
            #set uuid
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            #save the  image
            pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
            form.profile_pic.data.save(pic_path)
            
            
            #CHANGE  it to a string  to save to db
            current_user.profile_pic = pic_name       
            db.session.commit()
        
            flash('User updated successfully')
            return redirect(url_for('dashboard'))
        else:
            db.session.commit()
            flash('User updated successfully')
            return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.favorite_color.data = current_user.favorite_color
        form.username.data = current_user.username
      
    return render_template('dashboard.html', form=form)




@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    user_id = current_user.id
    if user_id == post_to_delete.poster.id or id== 2:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("blog post was delelted","success")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        
        except:
            flash("wooops there was a proble while deleting the blogs, Try Again")
    else:
         flash("you are'nt authorizes to delete post")
         posts = Posts.query.order_by(Posts.date_posted)
         return render_template("posts.html", posts=posts)


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
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data


        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated")
        return redirect(url_for('post', id=post.id))
    


    if current_user.id == post.poster.id or current_user.id == 2:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("you can't edit this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


#add post page

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if not current_user.is_authenticated:
     return redirect(url_for('posts'))

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
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
@login_required
def delete(id):
    if id == current_user.id:
     user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")
        return redirect(url_for('add_user'))  # Redirect to a different route after deletion
    except:
        flash("An error occurred while deleting the user", 'error')
        return redirect(url_for('add_user'))  # Redirect to a different route if an error occurs
    
    else:
        flash("sorry you can't delete this user")
        return redirect(url_for('dashboard'))




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
        name_to_update.about_author = request.form['about_author']

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





