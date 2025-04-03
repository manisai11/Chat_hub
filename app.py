from flask import Flask, render_template, redirect, url_for, session, g
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO
from auth import auth, User, users_collection
from chat import create_chat_blueprint  # Change import

app = Flask(__name__)
app.secret_key = b'6bde59df5ac94025a9388b3f9d118430'

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
app.register_blueprint(auth)
chat = create_chat_blueprint(socketio)  # Pass socketio to chat
app.register_blueprint(chat)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"username": user_id})
    return User(user["username"], user["username"]) if user else None

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def home():
    if session.get("remember_me") and current_user.is_authenticated:
        return redirect(url_for('main'))
    session.clear()
    return render_template('index.html')

@app.route('/main', methods=['POST', 'GET'])
@login_required
def main():
    return render_template('main.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html', user=current_user)

@app.route('/forgot_password')
def forgot_password():
    return render_template('fp.html')

@app.route('/register')
def register():
    return render_template('reg.html')

@app.route('/chat_page')
@login_required
def chat_page():
    return redirect(url_for('chat.chat_page'))

# Start the app with socketio
if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
