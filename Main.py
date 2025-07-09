from frontend.GUI import (
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
    GraphicalUserInterface
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Chargement des variables d’environnement
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

CHATLOG_PATH = r'Data\ChatLog.json'
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube"]

def ShowDefaultChatIfNoChats():
    try:
        os.makedirs("Data", exist_ok=True)
        if not os.path.exists(CHATLOG_PATH) or os.stat(CHATLOG_PATH).st_size < 5:
            with open(CHATLOG_PATH, 'w', encoding='utf-8') as file:
                json.dump([], file)

            os.makedirs(TempDirectoryPath(""), exist_ok=True)
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
    except Exception as e:
        print(f"[ERROR in ShowDefaultChatIfNoChats]: {e}")

def ReadChatLogJson():
    try:
        if not os.path.exists(CHATLOG_PATH) or os.stat(CHATLOG_PATH).st_size == 0:
            return []
        with open(CHATLOG_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"[JSON ERROR] Failed to read ChatLog.json: {e}")
        return []

def ChatlogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role")
        content = entry.get("content", "")
        if role == "user":
            formatted_chatlog += f"{Username} : {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname} : {content}\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
        data = File.read()
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File2:
            File2.write(data)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatlogIntegration()
    ShowChatsOnGUI()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")
    Decision = FirstLayerDMM(Query)

    print("\nDecision:", Decision, "\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = QueryModifier(str(queries))
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        try:
            with open(r"Frontend\Files\ImageGenerator.data", "w", encoding="utf-8") as file:
                file.write(f"{ImageGenerationQuery},True")
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"[ImageGeneration Error]: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                Answer = ChatBot(QueryModifier("Okay, Bye!"))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            if GetAssistantStatus() != "Available...":
                SetAssistantStatus("Available ...")
            sleep(0.2)

# ✅ LANCEMENT COMPLET
if __name__ == "__main__":
    InitialExecution()
    threading.Thread(target=FirstThread, daemon=True).start()
    GraphicalUserInterface()
