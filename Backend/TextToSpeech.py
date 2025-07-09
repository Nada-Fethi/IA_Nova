import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Charger les variables d'environnement
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice" )  # Voix par défaut

# Fonction asynchrone pour générer un fichier audio
async def TextToAudioFile(text: str) -> None:
    file_path = r"Data/speech.mp3"
    try:
        # S'assurer que pygame n'utilise pas encore le fichier
        pygame.mixer.quit()

        # Supprimer le fichier s'il existe déjà
        if os.path.exists(file_path):
            os.remove(file_path)

        # Générer le fichier audio
        communicate = edge_tts.Communicate(text, voice=AssistantVoice)
        await communicate.save(file_path)
    except Exception as e:
        print(f"Erreur dans TextToAudioFile: {e}")

# Fonction de lecture audio avec contrôle externe
def TTS(text: str, stop_func=lambda _: True) -> bool:
    try:
        # Générer fichier audio
        asyncio.run(TextToAudioFile(text))

        # Initialisation pygame
        pygame.mixer.init()
        pygame.mixer.music.load(r"Data/speech.mp3")
        pygame.mixer.music.play()

        # Boucle d'attente
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if not stop_func(True):
                break
            clock.tick(10)

        return True

    except Exception as e:
        print(f"Erreur dans TTS: {e}")
        return False

    finally:
        try:
            stop_func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Erreur dans le bloc finally: {e}")

# Fonction principale de Text-to-Speech
def TextToSpeech(text: str, stop_func=lambda _: True) -> None:
    sentences = text.strip().split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(sentences) > 4 and len(text) >= 250:
        partial_text = ". ".join(sentences[:2]).strip() + ". " + random.choice(responses)
        TTS(partial_text, stop_func)
    else:
        TTS(text.strip(), stop_func)

# Lancement direct du programme
if __name__ == "__main__":
    os.makedirs("Data", exist_ok=True)
    while True:
        user_input = input("Enter the text: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        TextToSpeech(user_input)
