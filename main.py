from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, name):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect ('/blog')

@app.route('/blog', methods=['GET', 'POST'])
def blog_posts():
    return render_template ('blog.html')

@app.route('/newpost', methods=['GET','POST'])
def create_post():
    if request.method == 'GET':
        return render_template ('create-post.html')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title.count() == 0:
            return redirect ('/newpost' + "?error=" + "Post title cannot be empty.")
        if body.count() == 0:
            return redirect ('/newpost' + "?error+" + "Post body cannot be empty.")
        blog = Blog(title=title, body=body)
        db.session.add(blog)
        db.session.commit()
        return redirect ('/blog' + '?id=') # return id of blog post

if __name__ == '__main__':
    app.run()