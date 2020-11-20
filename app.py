from flask import Flask, render_template, url_for, request, redirect, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import markdown
import bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./blog.db'
app.secret_key = os.urandom(12)

db = SQLAlchemy(app)
pwhash = b'$2b$15$I8ui9z0gGivDf9sis5wB6O0HElDZGkXldSLcKUyya0asurKRhO9tW' # Generated using brypt.hashpw()

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(30))
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)

@app.route('/all')
def all():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    return render_template('all.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add')
def add():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('add.html')

@app.route('/login', methods=['POST'])
def login():
    if bcrypt.checkpw(bytes(request.form['password'], 'utf-8'), pwhash):
        session['logged_in'] = True
    else:
        flash('Password incorrect!')
    return add()

@app.route('/submitpost', methods=['POST'])
def submitpost():
    if session.get('logged_in'):
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = markdown.markdown(request.form['content'])
        image = request.files['image']
        image.save('uploads/' + secure_filename(image.filename))

        post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now(), image=secure_filename(image.filename))

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)