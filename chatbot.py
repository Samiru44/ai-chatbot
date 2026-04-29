import os
from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Error: API key not found. Check your .env file.")
    exit()

# Initialize client
client = Groq(api_key=api_key)

# System role (important for your assignment context)
SYSTEM_PROMPT = """
You are a friendly tourism chatbot for Sri Lanka.
You help users with:
- Tourist places (Sigiriya, Ella, Kandy, Negombo)
- Travel tips
- Hotel suggestions
- Transport advice
Answer clearly and simply.
"""

# Store conversation history (memory)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

print("🌴 Sri Lanka Tourism Chatbot Ready!")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["quit", "exit"]:
        print("Bot: Goodbye! Have a nice trip!")
        break

    if not user_input:
        continue

    # Add user message
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        # Save bot response
        messages.append({"role": "assistant", "content": reply})

        print("Bot:", reply)

    except Exception as e:
        print("Error:", e)