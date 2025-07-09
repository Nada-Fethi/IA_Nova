from AppOpener import open as appopen, close
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKEY")
Username = env_vars.get("Username", "User")

# Validate API key
if not GroqAPIKey:
    raise ValueError("Missing 'GroqAPIKEY' in .env file")

# User agent for requests
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Base message context
messages = []
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {Username}. You're a content writer. You have to write content like letters."
}]

# ---------- FEATURES ----------

def GoogleSearch(topic):
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"[red]Error in GoogleSearch:[/red] {e}")
        return False

def Content(topic):
    def OpenNotePad(file_path):
        subprocess.Popen(["notepad.exe", file_path])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        messages.append({"role": "assistant", "content": answer})
        return answer.replace("</s", "")

    try:
        clean_topic = topic.replace("content ", "").strip()
        content_text = ContentWriterAI(clean_topic)
        os.makedirs("Data", exist_ok=True)
        file_path = f"Data/{clean_topic.lower().replace(' ', '')}.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content_text)
        OpenNotePad(file_path)
        return True
    except Exception as e:
        print(f"[red]Error in Content:[/red] {e}")
        return False

def YouTubeSearch(topic):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
        return True
    except Exception as e:
        print(f"[red]YouTubeSearch error:[/red] {e}")
        return False

def PlayYouTube(query):
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"[red]PlayYouTube error:[/red] {e}")
        return False

def OpenApp(app, sess=requests.session()):
    if app.lower() == "youtube":
        webbrowser.open("https://www.youtube.com")
        return True
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            soup = BeautifulSoup(html or "", 'html.parser')
            return [a.get('href') for a in soup.find_all('a', {'jsname': 'UWckNb'})]

        def search_google(query):
            headers = {"User-Agent": useragent}
            res = sess.get(f"https://www.google.com/search?q={query}", headers=headers)
            return res.text if res.status_code == 200 else None

        html = search_google(app)
        links = extract_links(html)
        if links:
            webopen(links[0])
            return True
        return False

def CloseApp(app):
    if "chrome" in app.lower():
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    action = actions.get(command.lower())
    if action:
        action()
        return True
    print(f"[yellow]Unknown system command:[/yellow] {command}")
    return False

# ---------- AUTOMATION CORE ----------

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        cmd = command.lower().strip()
        print(f"[green]Executing command:[/green] {cmd}")

        # Specific shortcut for opening YouTube
        if cmd == "open youtube":
            funcs.append(asyncio.to_thread(lambda: webbrowser.open("https://www.youtube.com")))
            continue

        if cmd.startswith("open ") and "open it" not in cmd and cmd != "open file":
            funcs.append(asyncio.to_thread(OpenApp, cmd.removeprefix("open ")))
        elif cmd.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd.removeprefix("close ")))
        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYouTube, cmd.removeprefix("play ")))
        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd.removeprefix("content ")))
        elif cmd.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search ")))
        elif cmd.startswith("youtube "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd.removeprefix("youtube ")))
        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd.removeprefix("system ")))
        else:
            print(f"[bold red]No Function Found for:[/bold red] {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True

# ---------- TEST ----------

if __name__ == "__main__":
    asyncio.run(Automation([
        "open youtube",
        "google search Morocco news",
        "play relaxing music",
        "system mute",
        "content write a letter to my teacher"
    ]))
