from flask import Flask, render_template, redirect, url_for, session, g, request, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from auth import auth, User, users_collection
from chat import create_chat_blueprint
import os

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

app = Flask(__name__)
app.secret_key = b'6bde59df5ac94025a9388b3f9d118430'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth)
chat = create_chat_blueprint(socketio)
app.register_blueprint(chat)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename}), 200

    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
