from flask import Flask, request, redirect, url_for, flash
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required \
    ,login_manager

app = Flask(__name__)
app.debug=True

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SECRET_KEY']=b'_5#y2L"F4Q8z\n\xec]/'
app.config['LOGIN_MESSAGE'] = 'login please'
app.config['LOGIN_MESSAGE_CATEGORY'] = 'info'

login_manager=LoginManager()
login_manager.init_app(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app=app,model_class=Base)

migrate=Migrate(app,db)

class Profile(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(20), unique=False, nullable=False)
    last_name= db.Column(db.String(20), unique=False, nullable=False)
    age=db.Column(db.Integer, nullable=False)
    dep=db.Column(db.String(20),unique=False, nullable=False)
    
    # def __repr__(self):
    #     return f'Name: {self.first_name}, Age: {self.age}'

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(250),unique=True,nullable=False)
    password=db.Column(db.String(250),nullable=False)


with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)

login_manager.login_view='login'
login_manager.login_message='login please'
login_manager.login_message_category='info'

@app.route('/add_data')
@login_required
def add_data():
    return render_template('add_profile.html')

@app.route('/add', methods=["POST"])
def add_Profile():
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    age=request.form.get('age')
    dep=request.form.get('department')
  
    if first_name !='' and last_name!='' and age is not None:
        p=Profile(first_name=first_name,last_name=last_name,age=age,dep=dep)
        db.session.add(p)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        user=User(username=request.form.get('username'),
                  password=request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('sign_up.html')

@app.route('/login',methods=['GET','POST'])
def login():
    # error=None
    if request.method=="POST":
        user=User.query.filter_by(username=request.form.get('username')).first()
    
        if user.password==request.form.get('password'):
            login_user(user)
            flash('You Were Successfully Logged In')
            next=request.args.get('next')
            return redirect(next or(url_for('index')))
        else:
            flash('Invalid Credentials')
            #error='Invalid Credentials'
      
    return render_template('login.html')

@app.route('/')
def index():
    Profiles=Profile.query.all()
    return render_template('index.html', Profiles=Profiles)

@app.route('/delete/<int:id>')
@login_required
def erase(id):
    data =Profile.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
@login_required
def get_data(id):
    profiles=Profile.query.get(id)
    return render_template('edit.html', profiles=profiles)

@app.route('/update/<int:id>',methods=['POST'])
def edit(id):
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    age=request.form.get('age')
    dep=request.form.get('department')
    
    profiles=Profile.query.get(id)
    
    if first_name !='' and last_name!='' and age is not None:
        profiles.first_name=first_name
        profiles.last_name=last_name
        profiles.age=age
        profiles.dep=dep
    db.session.commit()
    return redirect('/')

if __name__=='__main__':
    app.run()
    
'''Database Initialization:
Instead of creating tables inside the application context, 
consider using Flask-Migrate to manage database migrations. 
0This allows you to handle database schema changes more efficiently.'''