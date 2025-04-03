import random
import smtplib
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import users_collection, otp_collection  # Import DB from database.py

auth = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Use env variables
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_otp_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Password Reset OTP"

        body = f"Your OTP for password reset is: {otp}. It is valid for 5 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form  

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            login_user(User(username, username), remember=remember)
            session["remember_me"] = remember
            return redirect(url_for('main'))
        
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = users_collection.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            flash('Username or Email already exists', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "name": name,
            "username": username,
            "email": email,
            "mobile": mobile,
            "password": hashed_password
        })
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reg.html')
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        user = users_collection.find_one({"email": email})
        if not user:
            flash('Email not registered!', 'danger')
            return redirect(url_for('auth.forgot_password'))

        otp = random.randint(100000, 999999)
        otp_collection.update_one({"email": email}, {"$set": {"otp": otp}}, upsert=True)

        if send_otp_email(email, otp):
            flash('OTP sent to your email!', 'success')
            return redirect(url_for('auth.verify_otp', email=email))
        else:
            flash('Failed to send OTP. Try again!', 'danger')

    return render_template('fp.html')

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')  
    if request.method == 'POST':
        entered_otp = request.form['otp']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        otp_data = otp_collection.find_one({"email": email})
        if not otp_data or str(otp_data['otp']) != entered_otp:
            flash('Invalid or expired OTP!', 'danger')
            return redirect(url_for('auth.verify_otp', email=email))

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.verify_otp', email=email))

        hashed_password = generate_password_hash(new_password)
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        otp_collection.delete_one({"email": email})

        flash('Password reset successful! Login now.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('verify_otp.html', email=email)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    user_data = users_collection.find_one({"username": current_user.id})
    return render_template('profile.html', user=user_data)
