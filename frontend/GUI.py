import sys
import os
import json
from dotenv import dotenv_values
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout,
    QLabel, QFrame, QPushButton
)
from PyQt5.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QPixmap
from PyQt5.QtCore import Qt, QSize

# Load env variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\frontend\Files"
GraphicsDirPath = rf"{current_dir}\frontend\Graphics"

def GraphicsDirectoryPath(Filename):
    return rf"{GraphicsDirPath}\{Filename}"

def TempDirectoryPath(Filename):
    return rf"{TempDirPath}\{Filename}"

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath("Mic.data"), "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus() -> str:
    try:
        with open(TempDirectoryPath("Mic.data"), "r", encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "False"

def SetAssistantStatus(status):
    print(f"Assistant status: {status}")

def GetAssistantStatus() -> str:
    return "Available..."

def ShowTextToScreen(text):
    print(f"Screen Output: {text}")

def AnswerModifier(text: str) -> str:
    return text.strip().capitalize()

def QueryModifier(query: str) -> str:
    return query.strip().lower()

def MicButtonInitialled():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")


class InitialScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #0a0a0a;")

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('micro2.gif'))
        movie.setScaledSize(QSize(880, 460))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        layout.addWidget(self.gif_label)

        # self.label = QLabel("Hello, I am Alex")
        # self.label.setStyleSheet("""
        #     color: #e0e0e0;
        #     font-size: 20px;
        #     font-family: 'Segoe UI';
        #     font-weight: bold;
        #     margin-top: 20px;
        # """)
        # self.label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(self.label)

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('maca2.jpg')).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.icon_label)

        self.chat_button = QPushButton(" Go to Chat")
        self.chat_button.setCursor(Qt.PointingHandCursor)
        self.chat_button.setStyleSheet("""
            QPushButton {
                background-color: #0a0a0a;
                color: white;
                padding: 7px 10px;
                border-radius: 16px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
        """)
        self.chat_button.clicked.connect(self.go_to_chat)
        layout.addWidget(self.chat_button)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

    def set_stacked_widget(self, widget):
        self.stacked_widget = widget

    def go_to_chat(self):
        if hasattr(self, 'stacked_widget'):
            self.stacked_widget.setCurrentIndex(1)
            chat_screen = self.stacked_widget.widget(1)
            if hasattr(chat_screen, 'load_chat_from_json'):
                chat_screen.load_chat_from_json()

    def load_icon(self, path):
        pixmap = QPixmap(path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('micro.png'))
            MicButtonInitialled()
        else:
            self.load_icon(GraphicsDirectoryPath('micro2.gif'))
            MicButtonClosed()
        self.toggled = not self.toggled


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        self.setStyleSheet("background-color: #0a0a0a;")

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            background-color: #121212;
            color: #e0e0e0;
            border-radius: 12px;
            padding: 14px;
            font-family: 'Segoe UI';
            font-size: 14px;
        """)
        layout.addWidget(self.chat_text_edit)

        self.label = QLabel("Waiting for your command...")
        self.label.setStyleSheet("color: #888888; font-size:12px; margin-top: 8px;")
        self.label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.label)

        self.back_button = QPushButton(" Return to Voice Mode")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #1db954;
                color: white;
                padding: 6px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        self.back_button.clicked.connect(self.go_to_voice)
        layout.addWidget(self.back_button)

    def set_stacked_widget(self, widget):
        self.stacked_widget = widget

    def go_to_voice(self):
        if hasattr(self, 'stacked_widget'):
            self.stacked_widget.setCurrentIndex(0)

    def load_chat_from_json(self):
        try:
            with open("Data/Chatlog.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            formatted = ""
            for entry in data:
                if entry["role"] == "user":
                    formatted += f"🧑 {entry['content']}\n\n"
                elif entry["role"] == "assistant":
                    formatted += f"🤖 {entry['content']}\n\n"
            self.chat_text_edit.setPlainText(formatted.strip())
        except Exception as e:
            self.chat_text_edit.setPlainText("❌ Failed to load chat history.")
            print(f"[GUI Error] {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Assistantname} - Voice AI")
        self.setFixedSize(620, 520)
        self.setWindowIcon(QIcon(GraphicsDirectoryPath("micro2.gif")))
        self.setStyleSheet("background-color: #0a0a0a; border-radius: 12px;")

        self.stacked_widget = QStackedWidget(self)
        self.initial_screen = InitialScreen()
        self.chat_screen = ChatSection()

        self.initial_screen.set_stacked_widget(self.stacked_widget)
        self.chat_screen.set_stacked_widget(self.stacked_widget)

        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.chat_screen)
        self.setCentralWidget(self.stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    GraphicalUserInterface()
