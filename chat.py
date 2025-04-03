from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from database import messages_collection,users_collection  # Import DB from database.py

def create_chat_blueprint(socketio):
    chat = Blueprint("chat", __name__)

    @chat.route("/chat_history/<receiver>")
    @login_required
    def chat_history(receiver):
        """Fetch past messages between the current user and the receiver"""
        messages = list(messages_collection.find({
            "$or": [
                {"sender": current_user.username, "receiver": receiver},
                {"sender": receiver, "receiver": current_user.username}
            ]
        }).sort("timestamp", 1))  # Sort by time (oldest first)
        # Convert ObjectId to string for JSON response
        for message in messages:
            message["_id"] = str(message["_id"])
        return {"messages": messages}

    @chat.route("/check_user/<username>")
    @login_required
    def check_user(username):
        """Check if the username exists in the database."""
        user_exists = users_collection.find_one({"username": username}) is not None
        return jsonify({"exists": bool(user_exists)})
    
    @chat.route("/chat_page")
    @login_required
    def chat_page():
        return render_template("chat.html", user=current_user)

    @socketio.on("join")
    def handle_join(data):
        """User joins their private room using their username."""
        room = data.get("room")
        if not room:
            return
        join_room(room)
        emit("status", {"message": f"{current_user.username} joined the chat"}, room=room)

    @socketio.on("leave")
    def handle_leave():
        """User leaves their private room."""
        room = current_user.username
        leave_room(room)
        emit("status", {"message": f"{current_user.username} left the chat"}, room=room)

    @socketio.on("private_message")
    def handle_private_message(data):
        """Handles private messaging between users."""
        sender = current_user.username
        receiver = data["receiver"]
        message = data["message"]

        # Save message with timestamp
        messages_collection.insert_one({
            "sender": sender,
            "receiver": receiver,
            "message": message,
            "timestamp": datetime.utcnow()
        })

        emit("private_message", {"sender": sender, "message": message}, room=receiver)  # Notify receiver
        #emit("private_message", {"sender": sender, "message": message}, room=sender)    # Notify sender

    return chat
