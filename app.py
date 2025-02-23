from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import os
import webbrowser
import psutil  # For battery status & system info
import pyttsx3  # For text-to-speech
import time
import threading

app = Flask(__name__)
CORS(app)

# Load API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set this in your environment
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Set this in your environment
NEWS_API_KEY = os.getenv("0472b1eeb64548bb80dafcdb63bd2676")  # Set this in your environment

def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_message TEXT,
                            bot_response TEXT
                          )''')
        conn.commit()

init_db()

# AI Response Function
def get_groq_response(user_message):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = {
        "role": "system",
        "content": "You are an AI personal assistant named Banu, designed to help with queries efficiently."
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            system_prompt,
            {"role": "user", "content": user_message}
        ]
    }
    
    response = requests.post(GROQ_API_URL, json=data, headers=headers)
    try:
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "I couldn't process that.")
    except Exception as e:
        return f"API Error: {str(e)}"

# Get Battery Status
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery at {battery.percent}%"
    return "Battery status unavailable."

# Get CPU & Memory Status
def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    return f"CPU Usage: {cpu_usage}% | Memory Usage: {memory.percent}%"

# Get Current Time & Date
def get_time():
    return time.strftime("%I:%M %p")

def get_date():
    return time.strftime("%A, %B %d, %Y")

# Google Search
def search_google(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Searching Google for: {query}"

# Get Weather Information
def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        return f"The current weather in {city} is {temp}°C with {condition}."
    return "Unable to fetch weather data."

# Get Latest News
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        articles = response.json()["articles"][:5]
        news_summary = "\n".join([f"{i+1}. {a['title']}" for i, a in enumerate(articles)])
        return f"Here are the latest news headlines:\n{news_summary}"
    return "Unable to fetch news."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message").lower()

    if "open google" in user_message:
        webbrowser.open("https://www.google.com")
        return jsonify({"response": "Opening Google..."})
    
    elif "battery" in user_message:
        return jsonify({"response": get_battery_status()})

    elif "system status" in user_message:
        return jsonify({"response": get_system_status()})

    elif "search" in user_message:
        query = user_message.replace("search", "").strip()
        return jsonify({"response": search_google(query)})

    elif "time" in user_message:
        return jsonify({"response": f"Current time: {get_time()}"})

    elif "date" in user_message:
        return jsonify({"response": f"Today is {get_date()}"})

    elif "weather" in user_message:
        city = user_message.replace("weather in", "").strip()
        return jsonify({"response": get_weather(city)})

    elif "news" in user_message:
        return jsonify({"response": get_news()})

    bot_response = get_groq_response(user_message)

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (user_message, bot_response) VALUES (?, ?)", (user_message, bot_response))
        conn.commit()

    return jsonify({"response": bot_response})

@app.route("/history")
def history():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, bot_response FROM messages ORDER BY id DESC LIMIT 10")
        history = cursor.fetchall()
    
    formatted_history = [{"user": row[0], "bot": row[1]} for row in history]
    return jsonify(formatted_history)

if __name__ == "__main__":
    app.run(debug=True)





