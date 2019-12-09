from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title

def get_all_posts():
    return Blog.query.all()

def get_specific_post(id_num): #get by id
    return Blog.query.filter_by(id=id_num).all()

@app.route('/')
def index():
    return redirect ('/blog')

@app.route('/blog', methods=['GET'])
def blog_posts():
    if request.args.get('post'):
        post_id = request.args.get('post')
        return render_template('blog.html', blog=get_specific_post(post_id))
    return render_template ('blog.html', blog=get_all_posts())

@app.route('/newpost', methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error_list = []
        if title == "":
            error_list = error_list.append('title_error')
        if body == "":
            error_list = error_list.append('body_error')
        if error_list != []:
            return render_template ('create-post.html', errors=error_list)
        blog = Blog(title=title, body=body)
        db.session.add(blog)
        db.session.commit()
        return redirect ('/blog'+'?post='+str(blog.id))
    return render_template ('create-post.html', errors=[])

if __name__ == '__main__':
    app.run()