from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kjhvsdjhfvsjhdvf'

#---------------------------------------------------
#  || Database Classes for Blog & User Tables  ||
#---------------------------------------------------

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.relationship('User', backref='blog')

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    hash_pass = db.Column(db.String(120))
    blogs = db.Column(db.Integer, db.ForeignKey('blog.id'))

    def __init__(self, username, password):
        self.username = username
        self.hash_pass = make_pw_hash(password)

    def __repr__(self):
        return '<Blog %r>' % self.username

#---------------------------------------------------
#  ||             Helper Functions            ||
#---------------------------------------------------
def get_user():
    return User.query.filter_by(username=session['username']).first()

def get_user_posts(user): 
    return Blog.query.filter_by(owner_id=user).all()

def get_all_users(): 
    return User.query.all()

def get_specific_post(post_id):
    return Blog.query.filter_by(id=post_id).first()

#---------------------------------------------------
#  ||           Index & Navigation            ||
#---------------------------------------------------

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog_posts', 'login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    return render_template('index.html', users=get_all_users())

#---------------------------------------------------
#   ||       Register & Log In Pages       ||
#---------------------------------------------------

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.hash_pass):
            session['username'] = username
            flash("Logged in succesfully", 'info')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            flash("The username <strong>{0}</strong> is already registered".format(username), 'danger')

    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/')

#---------------------------------------------------
#    || Blog Functions for Logged-In Users ||
#---------------------------------------------------

@app.route('/blog', methods=['GET'])
def blog_posts():
    if request.args.get('user') != "":
        user_id = request.args.get('user')
        user_posts = get_user_posts(user_id)
        return render_template('singleUser.html', blog=user_posts, username=session['username'])
    #if request.args.get('post') != "":
      #  post_id = request.args.get('post')
       # return render_template('blog.html', blog=get_specific_post(post_id), username=session['username'])
    else:
        return redirect('/')

@app.route('/newpost', methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == "":
            flash("title cannot be empty")
        if body == "":
            flash("body cannot be empty")
        blog = Blog(title=title, body=body, owner=session['username'])
        db.session.add(blog)
        db.session.commit()
        return redirect ('/blog'+'?post='+str(blog.id))
    return render_template ('create-post.html')

if __name__ == '__main__':
    app.run()