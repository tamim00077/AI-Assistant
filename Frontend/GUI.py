from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, QPoint
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
old_chat_message = ""
# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how','what','who','where','when','why','which','whom','can you',"what's", "where's","how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)
    
def GetMicrophoneStatus():
    with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
        Status = file.read().strip()
    return Status

def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data','w',encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status
    
# Define placeholders for the missing functions
def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data','w', encoding='utf-8') as file:
        file.write(Text)
    
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 50, 20, 80)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            padding: 10px;
        """)
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor("#00ffaa")
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(rf"{GraphicsDirPath}\Jarvis.gif")
        max_gif_size_W = 400
        max_gif_size_H = 225
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("""
            color: #cdd6f4;
            font-size: 18px;
            font-family: 'Segoe UI', sans-serif;
            margin-right: 150px;
            border: none;
            margin-top: -20px;
        """)
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # Add mute button
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirPath + r'\Mic_on.png')
        new_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignRight)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        layout.addWidget(self.icon_label, alignment=Qt.AlignRight)

        font = QFont("Segoe UI", 14)
        font.setWeight(QFont.Medium)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            ChatSection {
                background-color: #1e1e2e;
                border-radius: 10px;
                padding: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a3b;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #00ffaa;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='#cdd6f4')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    def load_icon(self, path, width=80, height=80):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(rf'{GraphicsDirPath}\Mic_on.png', 80, 80)
            MicButtonInitiated()
        else:
            self.load_icon(rf'{GraphicsDirPath}\Mic_off.png', 80, 80)
            MicButtonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(15)
        formatm.setLeftMargin(15)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirPath + r'\Jarvis.gif')
        gif_label.setMovie(movie)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirPath + r'\Mic_on.png')
        new_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("""
            color: #cdd6f4;
            font-size: 20px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 500;
            margin-bottom: 20px;
        """)
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 100)
        self.setLayout(content_layout)

        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirPath + r'\Status.data', 'r', encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=80, height=80):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirPath + r'\Mic_on.png', 80, 80)
            MicButtonInitiated()
        else:
            self.load_icon(GraphicsDirPath + r'\Mic_off.png', 80, 80)
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
        """)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_screen = None
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Left spacer to push buttons to center
        layout.addStretch(1)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirPath + r'\Home.png')
        home_button.setIcon(home_icon)
        home_button.setText("   Home")
        home_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b4f;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                padding: 8px 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #1e1e2e;
            }
        """)
        home_button.clicked.connect(self.showInitialScreen)

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirPath + r'\Message.png')
        message_button.setIcon(message_icon)
        message_button.setText("   Message")
        message_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b4f;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                padding: 8px 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00ffaa;
                color: #1e1e2e;
            }
        """)
        message_button.clicked.connect(self.showMessageScreen)

        layout.addWidget(home_button)
        layout.addWidget(message_button)

        # Right spacer to balance centering
        layout.addStretch(1)

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirPath + r'\Minimize.png')
        minimize_button.setIcon(minimize_icon)
        minimize_button.setFlat(True)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b4f;
                border-radius: 8px;
                padding: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f1c232;
            }
        """)
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirPath + r'\Maximize.png')
        self.restore_icon = QIcon(GraphicsDirPath + r'\Restore.png')
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b4f;
                border-radius: 8px;
                padding: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f1c232;
            }
        """)
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirPath + r'\Close.png')
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3b3b4f;
                border-radius: 8px;
                padding: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
        """)
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#2a2a3b"))
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.offset is not None and self.draggable and not self.parent.isMaximized():
            self.parent.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = None
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximizeWindow()
            event.accept()

    def minimizeWindow(self):
        self.parent.showMinimized()

    def maximizeWindow(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent.showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent.close()

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 8  # Increased margin for better edge detection
        self.min_width = 800
        self.min_height = 600
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setMinimumSize(self.min_width, self.min_height)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
        """)
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            self.resize_edge = self.get_resize_edge(event.pos())
            if self.resize_edge:
                self.resizing = True
                self.start_pos = event.globalPos()
                self.start_geometry = self.geometry()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing and not self.isMaximized():
            delta = event.globalPos() - self.start_pos
            new_geometry = QRect(self.start_geometry)

            if self.resize_edge & Qt.LeftEdge:
                new_geometry.setLeft(self.start_geometry.left() + delta.x())
            if self.resize_edge & Qt.RightEdge:
                new_geometry.setRight(self.start_geometry.right() + delta.x())
            if self.resize_edge & Qt.TopEdge:
                new_geometry.setTop(self.start_geometry.top() + delta.y())
            if self.resize_edge & Qt.BottomEdge:
                new_geometry.setBottom(self.start_geometry.bottom() + delta.y())

            # Ensure minimum size
            if new_geometry.width() >= self.min_width and new_geometry.height() >= self.min_height:
                self.setGeometry(new_geometry)
        elif not self.isMaximized():
            edge = self.get_resize_edge(event.pos())
            if edge & (Qt.LeftEdge | Qt.RightEdge):
                self.setCursor(Qt.SizeHorCursor)
            elif edge & (Qt.TopEdge | Qt.BottomEdge):
                self.setCursor(Qt.SizeVerCursor)
            elif edge & (Qt.LeftEdge | Qt.TopEdge) or edge & (Qt.RightEdge | Qt.BottomEdge) or edge & (Qt.LeftEdge | Qt.BottomEdge) or edge & (Qt.RightEdge | Qt.TopEdge):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.resize_edge = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()

    def get_resize_edge(self, pos):
        if self.isMaximized():
            return 0  # No resizing when maximized
        rect = self.rect()
        edge = 0
        margin = self.resize_margin
        if pos.x() <= margin:
            edge |= Qt.LeftEdge
        if pos.x() >= rect.width() - margin:
            edge |= Qt.RightEdge
        if pos.y() <= margin:
            edge |= Qt.TopEdge
        if pos.y() >= rect.height() - margin:
            edge |= Qt.BottomEdge
        return edge

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())