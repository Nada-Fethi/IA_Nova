import cohere 
from rich import print
from dotenv import dotenv_values

# Charger la clé API Cohere depuis le fichier .env
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")

if not CohereAPIKey:
    print("[bold red]Error:[/bold red] No Cohere API key found in .env file")
    exit(1)

# Initialiser le client Cohere
co = cohere.Client(api_key=CohereAPIKey)

# Liste des catégories possibles
TASK_CATEGORIES = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "mute", "unmute", "volume",
    "brightness", "shutdown", "restart", "lock"
]

# Préambule (instructions) pour guider Cohere
PREAMBLE = """
You are a precise task classification system. Your ONLY job is to categorize user queries.
Respond with ONE of these formats:
- 'system [command]' for system operations (mute, volume, shutdown, etc.)
- 'general [query]' for conversational/informational queries
- 'realtime [query]' for queries needing live data
- 'open [app]' for opening applications
- 'close [app]' for closing applications
- 'play [content]' for playing media
- 'youtube search [query]' for YouTube searches
- 'reminder [details]' for setting reminders
- 'exit' for ending conversations

SPECIFIC SYSTEM COMMANDS INCLUDE:
- mute/unmute audio
- volume control
- brightness adjustment
- shutdown/restart
- lock screen
- any other system-level operation

RULES:
1. ALWAYS start with the most specific category
2. For system operations, use 'system' even if not exact match
3. Keep original wording after category
4. Default to 'general' only when clearly not actionable

Examples:
Input: "mute the computer"
Output: "system mute the computer"

Input: "can you lower the volume"
Output: "system lower the volume"

Input: "set brightness to 50%"
Output: "system set brightness to 50%"

Input: "hello there"
Output: "general hello there"
"""

# Fonction de classification
def classify_query(prompt: str) -> list:
    try:
        response = co.chat(
            model='command-r-plus',
            message=prompt,
            preamble=PREAMBLE,
            temperature=0.1,
            max_tokens=100
        )

        raw_response = response.text.strip().replace("\n", "").strip()

        # Priorité pour les commandes système
        system_keywords = ["mute", "unmute", "volume", "brightness", "shutdown", "restart", "lock"]
        if any(keyword in prompt.lower() for keyword in system_keywords):
            return [f"system {prompt}"]

        # Séparation des multiples commandes éventuelles
        tasks = [task.strip() for task in raw_response.split(",") if task.strip()]

        # Validation des catégories
        valid_tasks = []
        for task in tasks:
            matched = False
            for cat in TASK_CATEGORIES:
                if task.lower().startswith(cat.lower()):
                    valid_tasks.append(task)
                    matched = True
                    break
            if not matched:
                valid_tasks.append(f"general {task}")

        return valid_tasks

    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        return [f"general {prompt}"]

# Fonction appelée par Main.py
def FirstLayerDMM(prompt: str) -> list:
    return classify_query(prompt)

# Tester manuellement la classification
if __name__ == "__main__":
    print("[bold]Enhanced System Command Classifier[/bold] (type 'exit' to quit)")

    while True:
        try:
            user_input = input(">>> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("[bold red]Exiting...[/bold red]")
                break

            result = classify_query(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\n[bold red]Exiting...[/bold red]")
            break
        except Exception as e:
            print(f"[red]Error: {e}[/red]")
