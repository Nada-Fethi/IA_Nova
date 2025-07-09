from googlesearch import search
from groq import Groq
from json import load, dump, JSONDecodeError
import datetime
from dotenv import dotenv_values
import os

# تحميل متغيرات البيئة من .env
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKEY = env_vars.get("GroqAPIKEY")

if not GroqAPIKEY:
    raise ValueError("Missing GroqAPIKEY in .env")

# تهيئة عميل Groq
client = Groq(api_key=GroqAPIKEY)

# رسالة النظام التي تحدد تصرفات المساعد
System = f"""Hello, I am {Username}. You are {Assistantname}, a professional and helpful AI assistant with access to up-to-date information.
- Answer clearly, like a human.
- Do NOT say "according to the search results".
- Do NOT name sources.
- Do NOT mention your tools.
- Give full, professional answers.
"""

# مسار ملف سجل الدردشة
chatlog_path = "Data/Chatlog.json"
os.makedirs("Data", exist_ok=True)

def load_chatlog():
    """تحميل سجل الدردشة مع التعامل مع الملف التالف أو الفارغ"""
    if not os.path.exists(chatlog_path):
        with open(chatlog_path, "w", encoding="utf-8") as f:
            dump([], f)
        return []
    with open(chatlog_path, "r", encoding="utf-8") as f:
        try:
            return load(f)
        except JSONDecodeError:
            print("[RealtimeSearchEngine] ⚠️ Chatlog file corrupted or empty. Starting fresh.")
            return []

def save_chatlog(data):
    """حفظ سجل الدردشة"""
    with open(chatlog_path, "w", encoding="utf-8") as f:
        dump(data, f, indent=4)

def is_vague(prompt):
    """تحديد إذا كان الاستعلام غامض ويحتاج توضيح"""
    vague_words = ["more", "why", "how", "explain", "continue", "tell me more", "expand", "details"]
    return prompt.strip().lower() in vague_words

def GoogleSearch(query):
    """بحث في جوجل وإرجاع ملخص للنتائج"""
    try:
        results = list(search(query, advanced=True, num_results=5))
    except Exception as e:
        print(f"[GoogleSearch] Error during search: {e}")
        return "Sorry, I couldn't perform the search right now."

    Answer = ""
    for r in results:
        title = getattr(r, "title", "") or "No Title"
        desc = getattr(r, "description", "") or "No Description"
        Answer += f"{title}: {desc}\n\n"
    return Answer.strip()

def AnswerModifier(answer):
    """تنظيف الجواب من الأسطر الفارغة"""
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

def RealTimeInfo():
    """معلومات الوقت والتاريخ الحالية"""
    now = datetime.datetime.now()
    return f"Date and Time: {now.strftime('%A %d %B %Y, %H:%M:%S')}"

def RealtimeSearchEngine(prompt):
    """الدالة الرئيسية لتنفيذ البحث والإجابة"""
    messages = load_chatlog()
    messages.append({"role": "user", "content": prompt})

    # إذا كان السؤال غامض نستخدم آخر سؤال واضح
    if is_vague(prompt) and len(messages) > 1:
        query_for_search = next((m["content"] for m in reversed(messages[:-1]) if m["role"] == "user"), prompt)
    else:
        query_for_search = prompt

    # إجراء البحث على الويب
    search_data = GoogleSearch(query_for_search)

    # بناء المحادثة كاملة مع النظام والمعلومات والذاكرة
    full_messages = [
        {"role": "system", "content": System},
        {"role": "system", "content": f"Use this info to answer naturally:\n{search_data}"},
        {"role": "system", "content": RealTimeInfo()},
    ] + messages[-10:]  # احتفظ بآخر 10 رسائل

    # طلب الإجابة من Groq API
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=full_messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
        )
    except Exception as e:
        print(f"[Groq API] Error: {e}")
        return "Sorry, I am currently unable to respond."

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.strip().replace("</s", "")
    messages.append({"role": "assistant", "content": answer})
    save_chatlog(messages)

    return AnswerModifier(answer)

if __name__ == "__main__":
    print(f"Welcome {Username}! Type your query or 'exit'/'quit' to stop.")
    while True:
        prompt = input("Your question: ")
        if prompt.lower().strip() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = RealtimeSearchEngine(prompt)
        print(f"\n{Assistantname}: {response}\n")
