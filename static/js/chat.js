var socket = io.connect("http://" + document.domain + ":" + location.port);

// Get username from HTML
var username = document.getElementById("username").textContent.trim();
var chatRoom = "";

// Function to join chat
function joinChat() {
    chatRoom = document.getElementById("receiver").value;
    if (chatRoom === "") {
        alert("Enter a valid username to chat with!");
        return;
    }

    fetch(`/check_user/${chatRoom}`)
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            socket.emit("join", { room: username });

            fetch(`/chat_history/${chatRoom}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("chat-box").innerHTML = "";
                data.messages.forEach(msg => {
                    appendMessage(msg.sender, msg.message);
                });
            });

            document.getElementById("chat-box").innerHTML += `<b>Connected to ${chatRoom}</b><br>`;
        } else {
            alert("User does not exist! Please enter a valid username.");
        }
    })
    .catch(error => {
        console.error("Error checking user:", error);
    });
}

// Function to send a message
function sendMessage() {
    var message = document.getElementById("message").value;
    if (chatRoom === "") {
        alert("Start a chat first!");
        return;
    }
    if (message.trim() === "") {
        alert("Message cannot be empty!");
        return;
    }

    socket.emit("private_message", { receiver: chatRoom, message: message });

    appendMessage(username, message, "sent");

    document.getElementById("message").value = "";
}

// Function to append messages dynamically
function appendMessage(sender, message, type) {
    var chatBox = document.getElementById("chat-box");
    var msgDiv = document.createElement("div");
    msgDiv.classList.add("message");
    msgDiv.textContent = message;

    if (sender === username) {
        msgDiv.classList.add("sent");
    } else {
        msgDiv.classList.add("received");
    }

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Receive real-time messages
socket.on("private_message", function(data) {
    appendMessage(data.sender, data.message, "received");
});
