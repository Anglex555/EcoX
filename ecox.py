
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QTabWidget, QTabBar, QGroupBox, QTableWidget, QTableWidgetItem, QComboBox, QTextEdit
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
import json
import os
import datetime

import sqlite3

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Login'
        self.width = 900
        self.height = 600
        if os.path.exists("resolution.txt"):
            with open("resolution.txt", 'r') as file:
                resolution = file.read().strip()
                width, height = resolution.split('x')
                self.width = int(width)
                self.height = int(height)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
        background_label = QLabel(self)
        pixmap = QPixmap('background.png')
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, self.width, self.height)
        background_label.setScaledContents(True)

        self.white_block = QWidget(self)
        self.white_block.setFixedSize(300, 200)
        self.white_block.setStyleSheet("background-color: white; border-radius: 15px;")
        self.white_block_layout = QVBoxLayout(self.white_block)
        self.white_block_layout.setAlignment(Qt.AlignCenter)

        self.usernameLabel = QLabel('Username:', self.white_block)
        self.usernameInput = QLineEdit(self.white_block)
        self.usernameLabel.setStyleSheet("font-size: 16px; color: #333;")
        self.usernameInput.setStyleSheet("font-size: 14px; padding: 8px; border-radius: 5px; border: 1px solid #ccc;")

        self.passwordLabel = QLabel('Password:', self.white_block)
        self.passwordInput = QLineEdit(self.white_block)
        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.passwordLabel.setStyleSheet("font-size: 16px; color: #333;")
        self.passwordInput.setStyleSheet("font-size: 14px; padding: 8px; border-radius: 5px; border: 1px solid #ccc;")

        self.loginButton = QPushButton('Login', self.white_block)
        self.loginButton.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 24px;
                border-radius: 6px;
                background-color: #4CAF50;
                border: none;
                color: white;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.loginButton.clicked.connect(self.login)

        self.white_block_layout.addWidget(self.usernameLabel)
        self.white_block_layout.addWidget(self.usernameInput)
        self.white_block_layout.addWidget(self.passwordLabel)
        self.white_block_layout.addWidget(self.passwordInput)
        self.white_block_layout.addWidget(self.loginButton)

        layout = QVBoxLayout()
        layout.addWidget(self.white_block, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.attempts = 3

    def login(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        if self.checkCredentials(username, password):
            self.openMainMenu(username)
        else:
            self.attempts -= 1
            if self.attempts == 0:
                self.loginButton.setEnabled(False)
            QMessageBox.warning(self, 'Error', f'Invalid credentials. {self.attempts} attempts left.')

    def checkCredentials(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
        conn.close()
        if result:
            return True
        return False

    def openMainMenu(self, username):
        self.mainMenu = MainMenu(username)
        self.mainMenu.show()
        self.close()


class MainMenu(QWidget):
    def __init__(self, username):
        super().__init__()
        self.title = 'EcoX'
        self.width = 900
        self.height = 600
        self.username = username
        self.stage = 1

        if os.path.exists("resolution.txt"):
            with open("resolution.txt", 'r') as file:
                resolution = file.read().strip()
                width, height = resolution.split('x')
                self.width = int(width)
                self.height = int(height)
                
        if os.path.exists("stage"):
            with open("stage", 'r') as file:
                self.stage = int(file.read())
        self.selected_components = []
        if os.path.exists("selected_components"):
            with open("selected_components", 'r') as file:
                self.selected_components = json.load(file)
        print(self.selected_components)

        components = [
            'Сенсоры для определения преград',
            'Оперативная память',
            'Сенсоры для определения температуры',
            'Колеса',
            'Корпус',
            'Двигатель'
        ]
        self.component_dropdowns = []
        for component in components:
            dropdown = QComboBox()
            dropdown.addItem("Выбрать компонент")
            self.populateDropdown(dropdown, component)
            self.component_dropdowns.append(dropdown)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        self.tabs = QTabWidget(self)

        self.tab_bar = self.tabs.tabBar()
        self.tab_bar.setStyleSheet("""
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom-color: #aaa;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 50px;
                padding: 8px;
                margin-right: 2px;
                color: #333;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
        """)

        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Главная")
        self.initTab1()

        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "Разработка")
        self.initTab2()

        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, "Сборка")
        if self.stage >= 2:
            self.initTab3()
        
        self.tab4 = QWidget()
        self.tabs.addTab(self.tab4, "Тест")
        if self.stage >= 3:
            self.initTab4()
        
        self.tab5 = QWidget()
        self.tabs.addTab(self.tab5, "Производство")
        if self.stage >= 4:
            self.initTab5()

        self.tab6 = QWidget()
        self.tabs.addTab(self.tab6, "Выпуск")
        if self.stage >= 5:
            self.initTab6()

        self.tab7 = QWidget()
        self.tabs.addTab(self.tab7, "Этапы разработки")
        self.initTab7()

        self.tab8 = QWidget()
        self.tabs.addTab(self.tab8, "Прайс лист")
        self.initTab8()

        self.tab9 = QWidget()
        self.tabs.addTab(self.tab9, "Аккаунт")
        self.initTab9()

        self.tab10 = QWidget()
        self.tabs.addTab(self.tab10, "Настройки")
        self.initTab10()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        self.stage_label = QLabel("Этап разработки: {}".format(self.stage), self)
        self.stage_label.setStyleSheet("font-size: 14px; color: #333;")
        layout.addWidget(self.stage_label, alignment=Qt.AlignRight | Qt.AlignTop)

        self.setLayout(layout)

    def updateStageLabel(self):
        self.stage_label.setText("Этап разработки: {}".format(self.stage))

    def initTab1(self):
        layout = QVBoxLayout()

        ecow_label = QLabel("E", self)
        ecow_label.setStyleSheet("font-size: 48px; color: green; background-color: transparent;")
        co_label = QLabel("co", self)
        co_label.setStyleSheet("font-size: 48px; color: black; background-color: transparent;")
        x_label = QLabel("X", self)
        x_label.setStyleSheet("font-size: 48px; color: green; background-color: transparent;")

        ecow_layout = QHBoxLayout()
        ecow_layout.addWidget(ecow_label)
        ecow_layout.addWidget(co_label)
        ecow_layout.addWidget(x_label)
        ecow_layout.setAlignment(Qt.AlignCenter) 

        layout.addLayout(ecow_layout)

        info_label = QLabel(
            "Добро пожаловать в EcoX!\n"
            "Увеличьте свою эффективность вместе с EcoX!\n\n"
            "EcoX Enterprise Automation\n\n"
            "EcoX - это современная платформа для автоматизации предприятия.\n"
            "Мы предлагаем широкий спектр решений для оптимизации бизнес-процессов и повышения эффективности работы.\n"
            "Наши продукты включают в себя системы управления складом, производством, закупками и продажами.\n\n"
            "Мы стремимся к инновациям и созданию удобных и гибких инструментов для бизнеса.\n"
            "Присоединяйтесь к нам уже сегодня и увеличьте свою эффективность вместе с EcoX!", self)
        info_label.setStyleSheet("font-size: 16px; color: #333; text-align: center; background-color: #f0f0f0; padding: 20px; border-radius: 10px;")
        layout.addWidget(info_label)

        image_layout = QHBoxLayout()
        for i in range(3):
            image_label = QLabel(self)
            pixmap = QPixmap(f"image{i + 1}.jpg").scaledToWidth(300)
            image_label.setPixmap(pixmap)
            image_label.setStyleSheet("QLabel:hover { transform: scale(1.1); }") 
            image_layout.addWidget(image_label)
        layout.addLayout(image_layout)
        layout.setAlignment(Qt.AlignCenter)

        self.tab1.setLayout(layout)

    def initTab2(self):
        if self.stage == 1:
            layout = QVBoxLayout()

            stage_label = QLabel("Этап 1", self)
            stage_label.setStyleSheet("font-size: 22px; color: #333; font-weight: bold;")
            layout.addWidget(stage_label, alignment=Qt.AlignCenter)

            components = [
                'Сенсоры для определения преград',
                'Оперативная память',
                'Сенсоры для определения температуры',
                'Колеса',
                'Корпус',
                'Двигатель'
            ]

            self.component_dropdowns = []

            for component in components:
                group_box = QGroupBox(component)
                group_box_layout = QVBoxLayout()

                dropdown = QComboBox()
                dropdown.addItem("Выбрать компонент")
                self.populateDropdown(dropdown, component)

                group_box_layout.addWidget(dropdown)
                group_box.setLayout(group_box_layout)
                layout.addWidget(group_box)

                self.component_dropdowns.append(dropdown)

            start_button = QPushButton("Завершить Этап I.", self)
            start_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            start_button.clicked.connect(self.startDevelopmentProcess)
            layout.addWidget(start_button, alignment=Qt.AlignCenter)

            self.tab2.setLayout(layout)

        
    def populateDropdown(self, dropdown, component_type):
        conn = sqlite3.connect('robots.db')
        c = conn.cursor()
        c.execute("SELECT name FROM components WHERE price=?", (component_type,))
        components = c.fetchall()
        conn.close()

        for component in components:
            dropdown.addItem(component[0])

    def startDevelopmentProcess(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Engineer":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]

            if "Выбрать компонент" in self.selected_components:
                QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, выберите комплектующие для каждого поля.')
                return

            if self.stage == 1: 
                if os.path.exists("comment.txt"):
                    os.remove("comment.txt")
                self.stage = 2
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                self.initTab3()
                with open("selected_components", 'w') as file:
                    json.dump(self.selected_components, file)
                QMessageBox.about(self, 'Успешно', 'Этап 1 успешно завершён. \nПроект передан отделу производства опытных образцов.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только инженер может запускать этот процесс.')

    def initTab3(self):
        if self.stage == 2:
            layout = QVBoxLayout()

            stage_label = QLabel("2 этап", self)
            stage_label.setStyleSheet("font-size: 20px; color: #333; font-weight: bold;")
            layout.addWidget(stage_label, alignment=Qt.AlignCenter)

            description_label = QLabel("Сборка опытного образца", self)
            description_label.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(description_label, alignment=Qt.AlignCenter)

            selected_components_label = QLabel("Выбранные компоненты:", self)
            selected_components_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")
            layout.addWidget(selected_components_label)

            for component in self.selected_components:
                component_label = QLabel(component, self)
                component_label.setStyleSheet("font-size: 18px; color: #333;")
                layout.addWidget(component_label)

            successful_button = QPushButton("Модель успешна", self)
            successful_button.clicked.connect(self.startDevelopmentProcess2)
            successful_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(successful_button, alignment=Qt.AlignCenter)

            unsuccessful_button = QPushButton("Модель не успешна", self)
            unsuccessful_button.clicked.connect(self.reverseDevelopmentProcess2)
            unsuccessful_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #FF5733;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #FF5733;
                }
            """)
            layout.addWidget(unsuccessful_button, alignment=Qt.AlignCenter)

            self.tab3.setLayout(layout)

    def startDevelopmentProcess2(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Production Manager":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 2: 
                self.stage = 3
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                self.initTab4()
                QMessageBox.about(self, 'Успешно', 'Этап 2 успешно завершён. \nОпытный образец передан тестировщикам.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель производства может запускать этот процесс.')

    def reverseDevelopmentProcess2(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Production Manager":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 2: 
                self.stage = 1
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                QMessageBox.about(self, 'Успешно', 'Этап 2 не завершён. \nОпытный образец передан обратно инженерам.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель производства может запускать этот процесс.')

    def initTab4(self):
        if self.stage == 3:
            layout = QVBoxLayout()

            stage_label = QLabel("Этап 3", self)
            stage_label.setStyleSheet("font-size: 20px; color: #333; font-weight: bold;")
            layout.addWidget(stage_label, alignment=Qt.AlignCenter)

            description_label = QLabel("Тестирование опытного образца", self)
            description_label.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(description_label, alignment=Qt.AlignCenter)

            comment_label = QLabel("Комментарий:", self)
            comment_label.setStyleSheet("font-size: 16px; color: #333; font-weight: bold;")
            layout.addWidget(comment_label)

            self.comment_textedit = QTextEdit(self)
            layout.addWidget(self.comment_textedit)

            submit_button = QPushButton("Опытный образец прошёл тестирование", self)
            submit_button.clicked.connect(self.startDevelopmentProcess3) 
            submit_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(submit_button, alignment=Qt.AlignCenter)

            unsuccessful_button = QPushButton("Опытный образец не прошёл тестирование", self)
            unsuccessful_button.clicked.connect(self.reverseDevelopmentProcess3)
            unsuccessful_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #FF5733;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #FF5733;
                }
            """)
            layout.addWidget(unsuccessful_button, alignment=Qt.AlignCenter)

            self.tab4.setLayout(layout)

    def startDevelopmentProcess3(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Tester":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 3: 
                self.stage = 4
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                self.initTab4()
                QMessageBox.about(self, 'Успешно', 'Этап 3 успешно завершён. \nОпытный образец передан отделу производства.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель производства может запускать этот процесс.')

    def reverseDevelopmentProcess3(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Tester":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 3: 
                comment = self.comment_textedit.toPlainText()
                with open("comment.txt", 'w') as file:
                    file.write(comment)
                self.stage = 1
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                QMessageBox.about(self, 'Успешно', 'Этап 3 не завершён. \nОпытный образец передан обратно инженерам.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель производства может запускать этот процесс.') 

    def initTab5(self):
        if self.stage == 4:
            layout = QVBoxLayout()

            stage_label = QLabel("4 этап", self)
            stage_label.setStyleSheet("font-size: 20px; color: #333; font-weight: bold;")
            layout.addWidget(stage_label, alignment=Qt.AlignCenter)

            description_label = QLabel("Сборка опытного образца", self)
            description_label.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(description_label, alignment=Qt.AlignCenter)

            selected_components_label = QLabel("Выбранные компоненты:", self)
            selected_components_label.setStyleSheet("font-size: 16px; color: #333; font-weight: bold;")
            layout.addWidget(selected_components_label)

            for component in self.selected_components:
                component_label = QLabel(component, self)
                component_label.setStyleSheet("font-size: 16px; color: #333;")
                layout.addWidget(component_label)

            successful_button = QPushButton("Робот утверждён в серийный выпуск", self)
            successful_button.clicked.connect(self.startDevelopmentProcess4)
            successful_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(successful_button, alignment=Qt.AlignCenter)

            unsuccessful_button = QPushButton("Робот отклонён в серийный выпуск", self)
            unsuccessful_button.clicked.connect(self.reverseDevelopmentProcess4)
            unsuccessful_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #FF5733;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #FF5733;
                }
            """)
            layout.addWidget(unsuccessful_button, alignment=Qt.AlignCenter)

            self.tab5.setLayout(layout)

    def startDevelopmentProcess4(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Purchase Manager":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 4: 
                self.stage = 5
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                self.initTab4()
                QMessageBox.about(self, 'Успешно', 'Этап 4 успешно завершён. \nСерийное производство запущено.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель отдела производства может запускать этот процесс.')

    def reverseDevelopmentProcess4(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Purchase Manager":
            self.selected_components = [dropdown.currentText() for dropdown in self.component_dropdowns]
            if self.stage == 4: 
                self.stage = 1
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateStageLabel()
                QMessageBox.about(self, 'Успешно', 'Этап 4 не завершён. \nОпытный образец передан обратно инженерам.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель отдела производства может запускать этот процесс.')

    def initTab6(self):
        if self.stage == 5:
            layout = QVBoxLayout()

            stage_label = QLabel("5 этап", self)
            stage_label.setStyleSheet("font-size: 20px; color: #333; font-weight: bold;")
            layout.addWidget(stage_label, alignment=Qt.AlignCenter)

            description_label = QLabel("Расчёт цены и добавление  в прайс-лист в прайс-лист.", self)
            description_label.setStyleSheet("font-size: 18px; color: #333;")
            layout.addWidget(description_label, alignment=Qt.AlignCenter)

            selected_components_label = QLabel("Параметры дрона:", self)
            selected_components_label.setStyleSheet("font-size: 16px; color: #333; font-weight: bold;")
            layout.addWidget(selected_components_label)

            for component in self.selected_components:
                component_label = QLabel(component, self)
                component_label.setStyleSheet("font-size: 16px; color: #333;")
                layout.addWidget(component_label)

            price_label = QLabel("Введите стоимость:", self)
            price_label.setStyleSheet("font-size: 16px; color: #333; font-weight: bold;")
            layout.addWidget(price_label)
            
            self.price_input = QLineEdit(self)
            self.price_input.setStyleSheet("""
                font-size: 16px;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
            """)
            layout.addWidget(self.price_input)

            successful_button = QPushButton("Робот утверждён в серийный выпуск", self)
            successful_button.clicked.connect(self.startDevelopmentProcess5)
            successful_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 10px 24px;
                    border-radius: 6px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(successful_button, alignment=Qt.AlignCenter)

            self.tab6.setLayout(layout)

    def startDevelopmentProcess5(self):
        username = self.username

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=?", (username,))
        user_role = c.fetchone()[0]
        conn.close()

        if user_role == "Sales Manager":
            if self.stage == 5:
                price = self.price_input.text()
                
                conn = sqlite3.connect('robots.db')
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM robots")
                robot_count = c.fetchone()[0]
                
                drone_article = robot_count + 1
                
                c.execute("INSERT INTO robots (name, article, price, components, production_date, status) VALUES (?, ?, ?, ?, ?, ?)", (f"Дрон EcoX {drone_article}.0", drone_article, price, ", ".join(self.selected_components), datetime.date.today(), "В серийном производстве"))
                conn.commit()
                conn.close()
            
                self.stage = 1
                with open("stage", 'w') as file:
                    file.write(str(self.stage))
                self.updateRobotList()
                self.updateStageLabel()
                self.initTab4()
                QMessageBox.about(self, 'Успешно', 'Этап 5 успешно завершён. \nРазработка закончена.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Этот этап уже завершён.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Только руководитель отдела продаж может запускать этот процесс.')

    def initTab7(self):
        layout = QVBoxLayout()

        process_stages = [
            ("Этап I. Проектирование модели", "Инженер", "\nНа данном этапе проводится проектирование модели доставщика.", "Проектирование модели – занимаются инженеры."),
            ("Этап II. Сборка опытного образца", "Руководитель производства", "\nНа данном этапе собирается опытный образец доставщика. Если есть замечания, они отправляются инженерам.", "Сборка опытного образца – этим занимаются специалисты отдела производства. Если в процессе сборки появляются замечания к образцу модели, то они отправляются инженерам и процесс начинается заново. Если сборка прошла успешно, то осуществляется переход на следующий этап."),
            ("Этап III. Тестирование опытного образца", "Тестировщик", "\nНа данном этапе происходит тестирование опытного образца доставщика. Если есть замечания, они отправляются инженерам.", "Тестирование опытного образца – специалисты отдела тестирования. Если в процессе тестирования появляются замечания к образцу модели, то они отправляются инженерам и процесс начинается заново. Если тестирование прошло успешно, то осуществляется переход на следующий этап."),
            ("Этап IV. Утверждение в серийный выпуск", "Руководитель отдела производства", "\nНа данном этапе утверждается технологическая карта доставщика и его вводится в серийное производство.", "Утверждение нового робота в серийный выпуск. На данном этапе происходит утверждение технологической карты доставщика и ввод его в серийное производство."),
            ("Этап V. Расчет цены и добавление в прайс-лист", "Руководитель отдела продаж", "\nНа данном этапе устанавливается цена на доставщика и его добавляется в прайс-лист.", "Расчет цены на робота и добавление стоимости в прайс-лист. После утверждения на всех этапах для доставщика необходимо установить цену.")
        ]

        for stage, role, description, full_description in process_stages:
            stage_group = QGroupBox(stage)
            stage_group.setStyleSheet("""
                QGroupBox {
                    font-size: 16px;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 5px;
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #4CAF50;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                }
            """)
            stage_layout = QVBoxLayout()
            stage_label = QLabel(description)
            stage_label.setStyleSheet("font-size: 14px;")
            stage_layout.addWidget(stage_label)
            stage_group.setLayout(stage_layout)

            expand_button = QPushButton("Подробнее")
            expand_button.setStyleSheet("""
                QPushButton {
                    color: blue;
                    border: none;
                    text-decoration: underline;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: navy;
                }
            """)
            expand_button.clicked.connect(lambda _, desc=full_description: QMessageBox.information(self, "Подробности", desc))
            stage_layout.addWidget(expand_button)

            layout.addWidget(stage_group)

        self.tab7.setLayout(layout)

    def initTab8(self):
        layout = QVBoxLayout()

        self.price_list_table = QTableWidget()
        self.price_list_table.setColumnCount(3)
        self.price_list_table.setHorizontalHeaderLabels(["№", "Товар", "Цена"])

        self.price_list_table.setStyleSheet("""
            QTableWidget {
                background-color: #f0f0f0;
                alternate-background-color: #ffffff;
                color: #333333;
                font-weight: bold;
                font-size: 18px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 22px;
            }
        """)

        self.price_list_table.setColumnWidth(1, 500)

        self.price_list_table.verticalHeader().setDefaultSectionSize(75)

        layout.addWidget(self.price_list_table)

        self.tab8.setLayout(layout)

        self.updateRobotList()

    def updateRobotList(self):
        conn = sqlite3.connect('robots.db')
        c = conn.cursor()
        c.execute("SELECT * FROM robots WHERE status=?", ("В серийном производстве",))
        robots = c.fetchall()
        conn.close()

        self.price_list_table.setRowCount(0)

        for row_number, robot in enumerate(robots):
            self.price_list_table.insertRow(row_number)
            self.price_list_table.setItem(row_number, 0, QTableWidgetItem(str(robot[0]))) 
            name_and_components = f"{robot[1]}: {robot[4]}"
            name_and_components_item = QTableWidgetItem(name_and_components)
            name_and_components_item.setTextAlignment(Qt.AlignLeft)
            self.price_list_table.setItem(row_number, 1, name_and_components_item)
            self.price_list_table.setItem(row_number, 2, QTableWidgetItem(str(robot[3]))) 


    def getTesterComment(self):
        try:
            with open("comment.txt", 'r') as file:
                comment = file.read().strip()
            return comment
        except FileNotFoundError:
            return None

    def initTab9(self):
        layout = QVBoxLayout()

        header_label = QLabel("Аккаунт", self)
        header_label.setStyleSheet("font-size: 24px; color: #333; font-weight: bold;")
        layout.addWidget(header_label, alignment=Qt.AlignCenter)

        user_layout = QVBoxLayout()

        user_image_label = QLabel(self)
        pixmap = QPixmap('user_image.png') 
        pixmap = pixmap.scaledToWidth(200) 
        user_image_label.setPixmap(pixmap)
        user_image_label.setStyleSheet("border-radius: 50px;") 
        user_layout.addWidget(user_image_label, alignment=Qt.AlignCenter)

        account_label = QLabel(f"Вы вошли как: {self.username}", self)
        account_label.setStyleSheet("font-size: 20px;")
        account_label.setAlignment(Qt.AlignCenter) 
        user_layout.addWidget(account_label)

        layout.addLayout(user_layout)

        if self.username == "engineer":
            comment = self.getTesterComment()
            if comment:
                comment_label = QLabel(f"Комментарий от тестировщиков: {comment}", self)
                comment_label.setStyleSheet("font-size: 18px; color: #333; background-color: #FFC0CB; padding: 8px; border-radius: 6px;")
                layout.addWidget(comment_label)
            else:
                no_comment_label = QLabel("Комментариев нет", self)
                no_comment_label.setStyleSheet("font-size: 18px; color: #333; background-color: #D3D3D3; padding: 8px; border-radius: 6px;")
                layout.addWidget(no_comment_label)

        logout_button = QPushButton('Logout', self)
        logout_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px 24px;
                border-radius: 6px;
                background-color: #4CAF50;
                border: none;
                color: white;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button, alignment=Qt.AlignCenter)

        ecow_label = QLabel("E", self)
        ecow_label.setStyleSheet("font-size: 48px; color: green;")
        co_label = QLabel("co", self)
        co_label.setStyleSheet("font-size: 48px; color: black;")
        x_label = QLabel("X", self)
        x_label.setStyleSheet("font-size: 48px; color: green;")

        ecow_layout = QHBoxLayout()
        ecow_layout.addWidget(ecow_label)
        ecow_layout.addWidget(co_label)
        ecow_layout.addWidget(x_label)
        ecow_layout.setAlignment(Qt.AlignCenter)

        layout.addLayout(ecow_layout) 

        self.tab9.setLayout(layout)


    def logout(self):
        self.close()
        self.loginWindow = LoginWindow()
        self.loginWindow.show()

    def initTab10(self):
        resolution_label = QLabel("Выберите разрешение:", self)
        resolution_label.setStyleSheet("font-size: 20px; color: #333;")

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(["900x600", "1024x768", "1280x720", "1920x1080"]) 
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
                background-color: white;
            }
        """)

        save_button = QPushButton("Сохранить", self)
        save_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px 24px;
                border-radius: 6px;
                background-color: #4CAF50;
                border: none;
                color: white;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_button.clicked.connect(self.saveResolution)

        layout = QVBoxLayout()
        layout.addWidget(resolution_label)
        layout.addWidget(self.resolution_combo)
        layout.addWidget(save_button)
        self.tab10.setLayout(layout)

    def saveResolution(self):
        selected_resolution = self.resolution_combo.currentText()
        with open("resolution.txt", "w") as file:
            file.write(selected_resolution)
        QMessageBox.information(self, "Успех", "Разрешение успешно сохранено.\nПерезапустите приложение или авторизуйтесь заново для применения настроек.")

        
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'EcoX Enterprise Automation'
        self.width = 900
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)

        self.loginWindow = LoginWindow()
        self.loginWindow.show()

        self.createDatabase()
        self.createRobotsDatabase()

    def createDatabase(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
        c.execute('''INSERT OR IGNORE INTO users (username, password, role) VALUES 
                     ('admin', '11', 'Administrator'),
                     ('storekeeper', '11', 'Storekeeper'),
                     ('engineer', '11', 'Engineer'),
                     ('tester', '11', 'Tester'),
                     ('production_manager', '11', 'Production Manager'),
                     ('purchase_manager', '11', 'Purchase Manager'),
                     ('sales_manager', '11', 'Sales Manager')''')
        conn.commit()
        conn.close()

    def createRobotsDatabase(self):
        conn = sqlite3.connect('robots.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS components
                    (id INTEGER PRIMARY KEY,
                    name TEXT,
                    article TEXT,
                    price REAL,
                    components TEXT,
                    production_date DATE)''')

        # Добавление данных о комплектующих
        # components_data = [
        #     ("Сенсор для определения преград EC-23", "EC23-01", "Сенсоры для определения преград", 0.025, "17.08.2023"),
        #     ("Сенсор для определения преград ECPro-15", "ECPro15-01", "Сенсоры для определения преград", 0.023, "17.01.2022"),
        #     ("Сенсор для определения преград ECNorm-15", "ECNorm-15-01", "Сенсоры для определения преград", 0.30, "15.09.2023"),
        #     ("Сенсор для определения преград ECModern-95", "ECModern95-01", "Сенсоры для определения преград", 0.019, "01.02.2024"),
        #     ("Сенсор для определения преград EC-29", "EC29-01", "Сенсоры для определения преград", 0.027, "13.07.2023"),
        #     ("Оперативная память EC-OS-91", "ECOS91-01", "Оперативная память", 0.024, "25.05.2022"),
        #     ("Оперативная память EC-OS-125", "ECOS125-01", "Оперативная память", 0.030, "10.01.2021"),
        #     ("Оперативная память EC-OS-113", "ECOS113-01", "Оперативная память", 0.027, "02.03.2023"),
        #     ("Оперативная память EC-OS-99", "ECOS99-01", "Оперативная память", 0.020, "07.08.2022"),
        #     ("Оперативная память EC-OS-105", "ECOS105-01", "Оперативная память", 0.040, "15.01.2021"),
        #     ("Сенсор для определения температуры EC-Temp-50", "ECTemp50-01", "Сенсоры для определения температуры", 0.020, "03.09.2022"),
        #     ("Сенсор для определения температуры EC-Temp-47", "ECTemp47-01", "Сенсоры для определения температуры", 0.019, "01.03.2024"),
        #     ("Сенсор для определения температуры EC-Temp-54", "ECTemp54-01", "Сенсоры для определения температуры", 0.025, "10.12.2022"),
        #     ("Сенсор для определения температуры EC-Temp-59", "ECTemp59-01", "Сенсоры для определения температуры", 0.023, "25.02.2023"),
        #     ("Сенсор для определения температуры EC-Temp-57", "ECTemp57-01", "Сенсоры для определения температуры", 0.020, "23.01.2022"),
        #     ("Комплект колес 6 шт EC- wheels-15", "ECwheels15-01", "Колеса", 6.2, "07.02.2022"),
        #     ("Комплект колес 6 шт EC- wheels-23", "ECwheels23-01", "Колеса", 7.1, "15.08.2021"),
        #     ("Комплект колес 6 шт EC- wheels-50 (повышенной проходимости)", "ECwheels50-01", "Колеса", 10.1, "13.09.2023"),
        #     ("Комплект колес 6 шт EC- wheels-34", "ECwheels34-01", "Колеса", 5.6, "08.08.2023"),
        #     ("Комплект колес 6 шт EC- wheels-40", "ECwheels40-01", "Колеса", 4.9, "30.04.2022"),
        #     ("Комплект колес 6 шт EC- wheels-20", "ECwheels20-01", "Колеса", 6.3, "21.10.2023"),
        #     ("Корпус EC-body\\mach-34", "ECbodymach34-01", "Корпус", 15.4, "01.02.2021"),
        #     ("Корпус EC-body\\mach-25", "ECbodymach25-01", "Корпус", 18.2, "27.06.2022"),
        #     ("Корпус EC-body\\mach-47 (повышенной безопасности)", "ECbodymach47-01", "Корпус", 25.4, "23.03.2023"),
        #     ("Корпус EC-body\\mach-33", "ECbodymach33-01", "Корпус", 17.05, "21.09.2022"),
        #     ("Корпус EC-body\\mach-54 (повышенной безопасности)", "ECbodymach54-01", "Корпус", 24.25, "01.03.2023"),
        #     ("Корпус EC-body\\mach-33", "ECbody\\mach33-01", "Корпус", 20.04, "07.07.2022"),
        #     ("Двигатель EC- engine-05", "ECengine05-01", "Двигатель", 5.7, "01.03.2024"),
        #     ("Двигатель EC- engine-07", "ECengine07-01", "Двигатель", 8.1, "17.08.2023"),
        #     ("Двигатель EC- engine-11", "ECengine11-01", "Двигатель", 7.4, "03.09.2022"),
        #     ("Двигатель EC- engine-04", "ECengine04-01", "Двигатель", 6.8, "03.07.2023"),
        #     ("Двигатель EC- engine-09", "ECengine09-01", "Двигатель", 4.9, "31.01.2024"),
        #     ("Двигатель EC- engine-10", "ECengine10-01", "Двигатель", 5.7, "07.09.2023")
        # ] 


        # for component in components_data:
        #     c.execute("INSERT INTO components (name, article, price, components, production_date) VALUES (?, ?, ?, ?, ?)", component)

        # Создание таблицы роботов
        c.execute('''CREATE TABLE IF NOT EXISTS robots
                    (id INTEGER PRIMARY KEY,
                    name TEXT,
                    article TEXT,
                    price REAL,
                    components TEXT,
                    production_date DATE,
                    status TEXT)''')

        # Добавление данных о роботах    
        robots_data = [
            # Добавьте данные о роботах здесь
        ]

        for robot in robots_data:
            c.execute("INSERT INTO robots (name, article, price, components, production_date, status) VALUES (?, ?, ?, ?, ?, ?)", robot)

        conn.commit()
        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

# Пример комментария 
# Ужасное сопоставление компонентов. 
# Инженеры, вы вообще решили наугад комплектующие выбрать?
# Пройдено всего 2 из 10 тестов, внешний вид тоже огорчил...
# Переделывайте!

# Оценка: 2/10