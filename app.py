import os
import streamlit as st
import sqlite3
import uuid
from groq import Groq
from dotenv import load_dotenv

# -------------------- SETUP --------------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API key not found")
    st.stop()

client = Groq(api_key=api_key)

# -------------------- DATABASE --------------------
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_id TEXT,
    role TEXT,
    message TEXT
)
""")
conn.commit()

def save_message(chat_id, role, message):
    cursor.execute("INSERT INTO chats VALUES (?, ?, ?)", (chat_id, role, message))
    conn.commit()

def load_chat(chat_id):
    cursor.execute("SELECT role, message FROM chats WHERE chat_id=?", (chat_id,))
    return cursor.fetchall()

def get_chats():
    cursor.execute("SELECT DISTINCT chat_id FROM chats")
    return [row[0] for row in cursor.fetchall()]

# -------------------- SESSION --------------------
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "language" not in st.session_state:
    st.session_state.language = "Respond in English."

# -------------------- SIDEBAR --------------------
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id = str(uuid.uuid4())

for cid in get_chats():
    if st.sidebar.button(f"Chat {cid[:6]}", key=cid):
        st.session_state.chat_id = cid

# 🌐 Language selector
languages = {
    "English": "Respond in English.",
    "Sinhala": "සිංහලෙන් පිළිතුරු ලබාදෙන්න.",
    "Tamil": "தமிழில் பதிலளிக்கவும்."
}

selected_lang = st.sidebar.selectbox("🌐 Language", list(languages.keys()))
st.session_state.language = languages[selected_lang]

# -------------------- UI STYLE --------------------
st.markdown("""
<style>
body { background-color: #0b141a; }

.chat-container {
    max-width: 800px;
    margin: auto;
    padding-bottom: 80px;
}

.user-msg {
    background-color: #005c4b;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    margin-left: auto;
}

.bot-msg {
    background-color: #202c33;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.title("🌴 Sri Lanka Tourism Chatbot")

# -------------------- DISPLAY CHAT --------------------
messages = load_chat(st.session_state.chat_id)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for role, msg in messages:
    if role == "user":
        st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- VOICE SCRIPT --------------------
st.components.v1.html("""
<script>
function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        window.location.href = "?voice=" + encodeURIComponent(text);
    };

    recognition.start();
}
</script>
""", height=0)

# -------------------- INPUT --------------------
col1, col2 = st.columns([8,1])

with col1:
    user_input = st.chat_input("Type your message...")

with col2:
    if st.button("🎤"):
        st.markdown("<script>startListening()</script>", unsafe_allow_html=True)

# Capture voice input
query_params = st.query_params
if "voice" in query_params:
    user_input = query_params["voice"]
    st.query_params.clear()

# -------------------- PROCESS --------------------
if user_input:
    save_message(st.session_state.chat_id, "user", user_input)

    history = [{
        "role": "system",
        "content": f"""
You are a Sri Lanka tourism assistant.

- Give travel plans
- Suggest places
- Keep answers structured

IMPORTANT:
{st.session_state.language}
"""
    }]

    for role, msg in load_chat(st.session_state.chat_id):
        history.append({"role": role, "content": msg})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
        temperature=0.7,
        max_tokens=500
    )

    reply = response.choices[0].message.content

    save_message(st.session_state.chat_id, "assistant", reply)

    # 🔊 Voice output (no warning)
    st.markdown(f"""
    <script>
    var msg = new SpeechSynthesisUtterance(`{reply}`);
    speechSynthesis.speak(msg);
    </script>
    """, unsafe_allow_html=True)

    st.rerun()