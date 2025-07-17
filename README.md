# NovaIA
NovaIA is a smart voice assistant application built with Python and a modern GUI using PyQt5.
It is designed to interact with users through voice or text, interpret their queries using a Decision-Making Model (DMM), and respond using real-time search or AI-generated answers, while also allowing system automation tasks like opening apps.

<img width="620" height="516" alt="Capture d’écran 2025-07-10 002945" src="https://github.com/user-attachments/assets/72bd3c26-7741-4730-9f00-fbbee481e239" />

 ## Purpose of the Application

Enable voice interaction with the computer.

Automate tasks like launching apps, searching online, or performing system functions.

Provide real-time, internet-based answers using Google search + Groq’s LLM.

Present a clean, modern Graphical User Interface (GUI).

Save and display full chat history visually.

## Main Features


🎙️ Voice Interaction	: Uses microphone input to capture commands via SpeechRecognition.

🧠 Decision-Making Model (DMM)	: Classifies queries into: general, real-time search, or system task.

🌐 Real-Time Info Retrieval	: Uses googlesearch + Groq LLM to generate updated and human-like answers.

⚙️ System Automation :	Can open/close apps, run system commands (e.g., browser, notepad, YouTube).

💬 Chat History Memory :	Stores the conversation in a JSON file and renders it inside the GUI.

🖼️ PyQt5 GUI	: Features dynamic screens, animated buttons (GIF), light/dark modes.

🧭 Multi-page Navigation	: Toggle between voice mode and chat history with navigation buttons.

🔁 Smart Context Handling :	Understands vague commands (e.g., “continue”) by using past queries.



## Technical Stack

GUI :	PyQt5 with custom QWidgets, stacked pages

Voice Input :	SpeechRecognition + PyAudio

Text-To-Speech	: Edge-TTS (offline), or custom engine

LLM Response :	Groq’s LLaMA 3 API

Web Search : googlesearch (top 5 search result summaries)

Data Storage :	JSON file system for chat logs and assistant states

Automation Layer :	Python subprocess for system-level commands

State Management	: .data files for microphone and assistant statuses

## Target Users
NovaIA is built for:

Tech-savvy users who want a voice-controlled desktop assistant.

Students and researchers who need quick real-time information.

Developers interested in building or extending an AI assistant.

Busy professionals looking for hands-free control over routine tasks.

Accessibility users who benefit from voice interfaces over keyboard use.


