from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os
import errno

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKEY = env_vars.get("GroqAPIKEY")

# Initialize Groq client
client = Groq(api_key=GroqAPIKEY)

# System prompt
System = f"""
Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply in only English, even if the question is in Hindi, reply in English. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]
MAX_HISTORY = 20  # Limit chat history

CHATLOG_PATH = r"Data\Chatlog.json"

def ensure_chatlog_file():
    os.makedirs(os.path.dirname(CHATLOG_PATH), exist_ok=True)
    if not os.path.exists(CHATLOG_PATH):
        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump([], f)

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed.\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours :{now.strftime('%M')} minutes :{now.strftime('%S')} seconds.\n"
    )

def AnswerModifier(answer):
    return '\n'.join([line.strip() for line in answer.split('\n') if line.strip()])

def safe_write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            dump(data, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        if e.errno == errno.ENOSPC:  # No space left on device
            print("[ERROR] No space left on device. Free up space to save chat history.")
            return False
        else:
            raise

def ChatBot(Query, retry=False):
    ensure_chatlog_file()

    try:
        with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
            messages = load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load chatlog: {e}")
        messages = []

    messages.append({"role": "user", "content": Query})
    messages = messages[-MAX_HISTORY:]

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s", "").strip()
        messages.append({"role": "assistant", "content": Answer})

        if not safe_write_json(CHATLOG_PATH, messages):
            print("[WARNING] Answer generated but not saved due to disk space issue.")

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"[ERROR] {e}")
        if retry:
            return "Something went wrong. Please try again later."
        # Reset file if corrupted
        safe_write_json(CHATLOG_PATH, [])
        return ChatBot(Query, retry=True)

# Run in CLI
if __name__ == "__main__":
    print("Welcome! Ask me anything. (type 'exit', 'quit' or 'bye' to stop)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        response = ChatBot(user_input)
        print(f"{Assistantname}:", response)
