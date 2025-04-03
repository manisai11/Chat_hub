from flask import Flask, render_template, redirect, url_for, session, g
from flask_login import LoginManager, login_required, current_user
from auth import auth, User  

app = Flask(__name__)
app.secret_key = b'6bde59df5ac94025a9388b3f9d118430'  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  

app.register_blueprint(auth)

@login_manager.user_loader
def load_user(user_id):
    from auth import users_collection  
    user = users_collection.find_one({"username": user_id})
    if user:
        return User(user_id=user["username"])  
    return None

@app.before_request
def before_request():
    g.user = current_user  # Make current_user available in templates

@app.route('/')
def home():
    if session.get("remember_me") and current_user.is_authenticated:
        return redirect(url_for('main'))
    session.clear()  # Clear session if not remembered
    return render_template('index.html')

@app.route('/main', methods=['POST', 'GET'])
@login_required
def main():
    return render_template('main.html')  

@app.route('/chat')
@login_required
def chat():
    return render_template('gpt.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html',user=current_user)

@app.route('/forgot_password')
def forgot_password():
    return render_template('fp.html')

@app.route('/register')
def register():
    return render_template('reg.html')

if __name__ == '__main__':
    app.run(debug=True)
