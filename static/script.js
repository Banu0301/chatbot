function sendMessage() {
    let userInput = document.getElementById("userInput").value;
    if (userInput.trim() === "") return;

    let chatbox = document.getElementById("chatbox");

    // Add user message
    let userMessage = `<div class="message user-message">
        <div class="avatar user-avatar"></div>
        <div class="text-bubble">${userInput}</div>
    </div>`;
    chatbox.innerHTML += userMessage;

    // Send request to Flask backend
    fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message: userInput }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        let botMessage = `<div class="message bot-message">
            <div class="avatar bot-avatar"></div>
            <div class="text-bubble">${data.response}</div>
        </div>`;
        chatbox.innerHTML += botMessage;
        chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll
    });

    document.getElementById("userInput").value = "";
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function startVoiceRecognition() {
    fetch("/voice", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        document.getElementById("userInput").value = data.message;
        sendMessage();
    });
}



function loadHistory() {
    fetch("/history")
        .then(response => response.json())
        .then(data => {
            let chatbox = document.getElementById("chatbox");
            chatbox.innerHTML = "";  // Clear chatbox before loading history

            data.forEach(chat => {
                chatbox.innerHTML += `<div><strong>You:</strong> ${chat.user}</div>`;
                chatbox.innerHTML += `<div><strong>AI:</strong> ${chat.bot}</div>`;
            });
        })
        .catch(error => console.error("Error loading history:", error));
}
