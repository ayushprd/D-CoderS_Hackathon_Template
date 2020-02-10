from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(800), nullable=False)
    date = db.Column(db.String(15), nullable=False)


    def __repr__(self):
        return '<Task %r>' % self.id

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        event_name = request.form['name']
        event_desc = request.form['desc']
        event_date = request.form['date']
        new_event = Todo(name=event_name, desc=event_desc, date=event_date)

     
        
			

        
        try:
            db.session.add(new_event)
            db.session.commit()

            return redirect('/')

        except:
            return 'there was an error'

    else:
       events = Todo.query.all()
        #rows = Todo.query.count()
       names = []
       descs = []
       dates = []
       for event in events:
           names.append(event.name)
           descs.append(event.desc)
           dates.append(event.date)

       

       d = {'event': [{'names': a, 'descs': t, 'dates': ds} for a, t, ds in zip(names, descs, dates)]}


       car = 5
       peter = Todo.query.filter_by(name='Kaalrarv').first()
       return render_template('Current.html', names=names, descs=descs, dates=dates, peter=peter) # ,events=events, rows=rows)



@app.route('/past', methods=['POST', 'GET'])
def past():
    
       events = Todo.query.all()
        #rows = Todo.query.count()
       names = []
       descs = []
       dates = []
       for event in events:
           names.append(event.name)
           descs.append(event.desc)
           dates.append(event.date)

    
       return render_template('Past.html', names=names, descs=descs, dates=dates) # ,events=events, rows=rows)







@app.route('/upcoming', methods=['POST', 'GET'])
def upcoming():
    
       events = Todo.query.all()
        #rows = Todo.query.count()
       names = []
       descs = []
       dates = []
       for event in events:
           names.append(event.name)
           descs.append(event.desc)
           dates.append(event.date)

    
       return render_template('Upcoming.html', names=names, descs=descs, dates=dates) # ,events=events, rows=rows)







@app.route('/delete/<int:id>')
def delete(id):
    event_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(event_to_delete)
        db.session.commit()
        return redirect('/admin')
    except:
        return "there was a problem deleting that event"



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event = Todo.query.get_or_404(id)

    if request.method == 'POST':
        event.name = request.form['name']
        event.desc = request.form['desc']
        event.date = request.form['date']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "there was an issue updating"

    else:
        return render_template('update.html', event=event)




















@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        event_name = request.form['name']
        event_desc = request.form['desc']
        event_date = request.form['date']
        new_event = Todo(name=event_name, desc=event_desc, date=event_date)

     
          
        try:
            db.session.add(new_event)
            db.session.commit()

            return redirect('/')

        except:
            return 'there was an error'

    else:
       events = Todo.query.all()
        #rows = Todo.query.count()
       names = []
       descs = []
       dates = []
       for event in events:
           names.append(event.name)
           descs.append(event.desc)
           dates.append(event.date)

       #return render_template('Current.html', names=names, descs=descs, dates=dates, peter=peter) # ,events=events, rows=rows)
    return render_template('admin.html', events=events) 



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user :
            if check_password_hash(user.password,form.password.data):
                login_user(user,remember=form.remember.data)
                return redirect(url_for('admin'))
            return '<h1>Invalid username or password</h1>'
       # return '<h1>' + form.username.data + ' ' + form.password.data+ '</h1>'

    return render_template('login_page.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

        #return '<h1>' + form.username.data + ' '+ form.email.data +' '+ form.password.data+ '</h1>'

    return render_template('signup.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def searching():
    if request.method == 'POST':
        squery = request.form['ing']
        sanswer = Todo.query.filter_by(name=squery).first()
        
        return render_template('result.html', sanswer=sanswer)
    else:
        return render_template('search.html')










if __name__ == "__main__":
    app.run(debug=True)



