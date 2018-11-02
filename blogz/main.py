
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpass@localhost:3307/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='jfj3778hakd'

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(120))
    post_text = db.Column(db.String(500))
    writer_id = db.Column(db.Integer,db.ForeignKey('writer.writer_id'))
    
    def __init__(self, post_title, post_text, writer):        
        self.post_title = post_title
        self.post_text = post_text
        self.writer=writer
    
class Writer(db.Model):
    writer_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='writer')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#@app.before_request
#def require_login():
    #allowed_routes = ['login', 'register']
    #if request.endpoint not in allowed_routes and 'username' not in session:
     #   return redirect ('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('username') is not None:
        flash("You are already logged in.")
        return redirect ('/')
    if request.method == 'POST':             
        username = request.form['username']
        password = request.form['password']
        writer = Writer.query.filter_by(username=username).first()        
        if writer and writer.password == password:
            session['username'] = username
            flash("You are now logged in!")
            return redirect ('/newpost')
        else:
            flash("User password incorrect, or user does not exist.")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']        
        if username == '' or password == '' or password != verify or len(username) < 3 or len(username) < 3:
            flash('Some fields were left blank, or the passwords did not match. Make sure you choose a username and password 3 characters or longer.')
            return render_template('register.html')
        else:      
             
            existing_writer = Writer.query.filter_by(username=username).first()
            if not existing_writer:
                new_writer = Writer(username,password)
                db.session.add(new_writer)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:              
                error1 = "User already exists. Try, try again."
                return render_template('register.html', error1=error1)       
                
    return render_template('register.html')

@app.route('/logout')
def logout():
    if session.get('username') is not None:
        del session['username']
        flash('You have logged out.')
        return redirect('/blogusers')           
    else:
        flash('No user is currently logged in.')
        return redirect('/blogusers')
        
@app.route('/', methods=['POST', 'GET'])
def index():

    return redirect('/blogusers')

@app.route('/blogusers', methods=['POST','GET'])
def show_all_blog_users():
    writers = Writer.query.all()
    
    return render_template('blogusers.html',writers=writers)

@app.route('/blog', methods=['POST','GET'])
def show_all_blogs():

    posts = Post.query.all()
    authors = Writer.query.all()
    
    
    

    
    
    if posts == '':
        noposts = "There are no posts to show."
        return render_template('blog.html',title="Welcome to the Blog!", noposts=noposts)
    else:
        return render_template('blog.html',title="Welcome to the Blog!", posts=posts, authors=authors)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    
    if session.get('username') is not None:
        current_author = session['username']       
        if request.method == 'POST':
            post_title = ''
            post_text = ''
            post_title = request.form['blog_post_title']
            post_text = request.form['blog_post_text']
            post_author = Writer.query.filter_by(username=session['username']).first()
            if post_title == '' or post_text == '':
                flash("You left one of the fields blank. Try, try again.")
                return render_template('newpost.html', blog_post_title=post_title,blog_post_text=post_text, current_author=current_author)
            else:
                newPost = Post(post_title, post_text, post_author)
                db.session.add(newPost)                
                db.session.commit()        
                writer_id = post_author.writer_id
                author_name = post_author.username
                return render_template('post.html',blog_post_title = post_title,blog_post_text=post_text, author_name = author_name, writer_id=writer_id)
        else:
            return render_template('newpost.html', current_author=current_author) 

    else:
        flash("You need to be logged in to do that.")
        return render_template("login.html")    
    

@app.route('/display_post', methods=['GET', 'POST'])
def display_post():
    blog_id = request.args.get('post_id_req')
    blog_content = Post.query.filter_by(post_id=blog_id).first()
    blog_title = blog_content.post_title
    blog_text = blog_content.post_text
    post_writer_id = blog_content.writer_id
    post_writer_username_get = Writer.query.filter_by(writer_id=post_writer_id).first()
    post_writer_username = post_writer_username_get.username
    return render_template('post.html',blog_post_title = blog_title,blog_post_text=blog_text, writer_id= post_writer_id, author_name=post_writer_username)
    

@app.route('/authorposts', methods=['GET', 'POST'])
def display_post_by_author():
    author_ID_number_get = request.args.get('writer_id_req')
    authors = Writer.query.filter_by(writer_id=author_ID_number_get).first() 
    author_name_only = authors.username 
    posts = Post.query.filter_by(writer_id=author_ID_number_get).all()    
    return render_template('authorposts.html', posts=posts, author_name=author_name_only)

if __name__ == "__main__":
    app.run()