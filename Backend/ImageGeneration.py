import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# 📁 Chemins
DATA_FOLDER = r"Data"
STATUS_FILE = r"Frontend\Files\ImageGeneration.data"

# 🔐 API Hugging Face Stable Diffusion
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {
    "Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"
}

# 📤 Requête vers l'API Hugging Face
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# 🧠 Génération des images
async def generate_images(prompt: str):
    tasks = []
    prompt_clean = prompt.replace(" ", "_")

    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    results = await asyncio.gather(*tasks)

    os.makedirs(DATA_FOLDER, exist_ok=True)
    for idx, image_bytes in enumerate(results, 1):
        path = os.path.join(DATA_FOLDER, f"{prompt_clean}{idx}.jpg")
        with open(path, "wb") as f:
            f.write(image_bytes)

# 📷 Affichage des images générées
def open_images(prompt):
    prompt_clean = prompt.replace(" ", "_")
    for i in range(1, 5):
        image_path = os.path.join(DATA_FOLDER, f"{prompt_clean}{i}.jpg")
        try:
            img = Image.open(image_path)
            print(f"[Image] → {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"[Erreur] Impossible d'ouvrir l'image : {image_path}")

# 🎯 Fonction principale de génération et ouverture
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# 🔄 Boucle de surveillance du fichier de génération
if __name__ == "__main__":
    print("[⏳] En attente d'une requête d'image...")

    while True:
        try:
            with open(STATUS_FILE, "r") as f:
                data = f.read().strip()
            prompt, status = data.split(",")

            if status.lower() == "true":
                print(f"[⚙️] Génération d'images pour : {prompt}")
                GenerateImages(prompt)

                with open(STATUS_FILE, "w") as f:
                    f.write("False,False")
                print("[✅] Images générées et affichées.")
                break
            else:
                sleep(1)
        except :
                pass