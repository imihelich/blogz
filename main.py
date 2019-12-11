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
class User(db.Model): #CANNOT SEE BLOG INFO FROM USER - ONE USER HAS MULTIPLE BLOG POSTS

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    hash_pass = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.hash_pass = make_pw_hash(password)

class Blog(db.Model): # Author ID can be accessed from Blog

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

#---------------------------------------------------
#  ||             Helper Functions            ||
#---------------------------------------------------
def get_all_users():
    return User.query.all()

def get_all_posts():
    return Blog.query.all()
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
    return render_template('index.html', users=get_all_users(), log_user=session.get('username',''))

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
    return render_template('login.html', log_user="")

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

    return render_template('signup.html', log_user="")


@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/')

#---------------------------------------------------
#    || Blog Functions for Logged-In Users ||
#---------------------------------------------------

@app.route('/blog', methods=['GET'])
def blog_posts():

    if request.args.get('user'): #WORKING PERFECTLY - NO TOUCHIE (finds posts to feed in by user id)
        author_user = User.query.filter_by(username=request.args.get('user')).first()
        post_list = Blog.query.filter_by(owner=author_user).all()
        return render_template('singleUser.html', blog=post_list, log_user=session.get('username',''))

    if request.args.get('id'): #GIVEN THE POST ID RETRIEVE WHOLE POST
        post_id = int(request.args.get('id'))
        user_post = Blog.query.get(post_id)
        return render_template('blog.html', blog=user_post, log_user=session.get('username',''))

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

        owner = User.query.filter_by(username=session['username']).first()
        blog = Blog(title=title, body=body, owner=owner)
        db.session.add(blog)
        db.session.commit()
        return redirect ('/blog'+'?id='+str(blog.id))

    return render_template ('create-post.html', log_user=session['username'])

if __name__ == '__main__':
    app.run()