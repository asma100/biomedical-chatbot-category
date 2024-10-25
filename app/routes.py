from flask import Flask, render_template, url_for, flash, redirect, request, send_file, jsonify
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from app.gemini2 import ask_question
from flask import Flask




@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('chat'))
    return render_template('landingpage.html')


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    query = None
    answer = None

    if request.method == 'POST':
        category =request.form.get('category')
        device=request.form.get('device')
        query = request.form.get('query')
        if query:
            answer = ask_question(query,category)

    return render_template('chatbot.html', query=query, answer=answer)

@app.route('/get_response', methods=['GET', 'POST'])
def get_response():
    data = request.get_json()
    query = data.get('query')
    category = data.get('category')
    device = data.get('device')
    if query:
        answer = ask_question(query,category,device)
        return jsonify({'response': answer})
    return jsonify({'response': 'No query provided.'})

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About')
@app.route("/educational", methods=['GET', 'POST'])
def educational():
    return render_template('educational.html', title='educational')
@app.route("/imaging", methods=['GET', 'POST'])
def imaging():
    return render_template('imaging.html', title='imaging')
@app.route("/ICU", methods=['GET', 'POST'])
def ICU():
    return render_template('ICU.html', title='ICU')
@app.route("/laboratory", methods=['GET', 'POST'])
def laboratory():
    return render_template('laboratory.html', title='laboratory')
@app.route("/surgical", methods=['GET', 'POST'])
def surgical():
    return render_template('surgical.html', title='surgical')




@app.route("/", methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))