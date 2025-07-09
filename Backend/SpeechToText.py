from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Charger les variables d'environnement depuis le fichier .env
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Valeur par défaut "en"

# Code HTML pour la reconnaissance vocale
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Remplacer la langue dans le code HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Créer le dossier Data s'il n'existe pas et écrire le fichier HTML
os.makedirs("Data", exist_ok=True)
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Récupérer le chemin absolu du fichier HTML
current_dir = os.getcwd()
Link = os.path.join(current_dir, "Data", "Voice.html")

# Configurer les options Chrome pour Selenium
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialiser le driver Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Dossier temporaire pour le status
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status: str):
    """Écrit le status dans un fichier."""
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query: str) -> str:
    """Ajoute ponctuation et majuscule à la requête."""
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(new_query.startswith(word) for word in question_words):
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
        else:
            new_query = new_query[:-1] + "?"
    else:
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "."
        else:
            new_query = new_query[:-1] + "."
    return new_query.capitalize()

def UniversalTranslator(Text: str) -> str:
    """Traduit le texte en anglais."""
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition() -> str:
    """Lance la reconnaissance vocale et retourne la transcription modifiée."""
    driver.get(f"file:///{Link}")
    time.sleep(1)  # Attendre le chargement
    driver.find_element(By.ID, "start").click()
    SetAssistantStatus("Listening...")

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                driver.find_element(By.ID, "end").click()
                SetAssistantStatus("Processing...")
                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    translated = UniversalTranslator(Text)
                    return QueryModifier(translated)
        except Exception:
            pass
        time.sleep(0.1)  # Petit délai pour limiter CPU

if __name__ == "__main__":
    while True:
        text = SpeechRecognition()
        print(text)
