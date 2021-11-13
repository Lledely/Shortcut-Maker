import sys
import sqlite3
import keyboard as _keyboard
import time as _time
import csv

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QWidget

from add_shortcut_widget import Ui_Form as Add_UI
from autogui_gui import Ui_MainWindow as Main_UI
from delete_shortcut_widget import Ui_Form as Delete_UI
from info_widget import Ui_Form as Info_UI


class Main(QMainWindow, Main_UI):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Shortcuts Maker")
        self.database = QSqlDatabase.addDatabase('QSQLITE')
        self.DATABASE_NAME = "shortcuts_db.sqlite"
        self._check = True
        self.DELAY = 10
        self._connection = sqlite3.connect(self.DATABASE_NAME)
        self._cursor = self._connection.cursor()
        self._shorts = self._cursor.execute("""SELECT key_to_press, combination FROM shortcuts""").fetchall()
        self.shortcuts = {}
        for i in self._shorts:
            self.shortcuts[i[0]] = i[1]

        self.initUI()

    def initUI(self):
        self.add_shortcut.clicked.connect(self.add)
        self.delete_shortcut.clicked.connect(self.delete)
        self.set_delay.clicked.connect(self.set_time_delay)
        self.start_program.clicked.connect(self.start)
        self.get_info_button.clicked.connect(self.get_info)
        self.csv_parse_button.clicked.connect(self.parse_to_csv)
        
        self.database.setDatabaseName(self.DATABASE_NAME)
        self.database.open()

        model = QSqlTableModel(self, self.database)
        model.setTable('shortcuts')
        model.select()

        self.shortcuts_view.setModel(model)

        self.error_label.hide()

    def add(self):
        self.database.close()
        self.adding_new_shortcut = AddShortcutWidget(self, self.DATABASE_NAME)
        self.adding_new_shortcut.show()
        self.setEnabled(False)

    def delete(self):
        self.database.close()
        self.delete_shortcut = DeleteShortcutWidget(self, self.DATABASE_NAME)
        self.delete_shortcut.show()
        self.setEnabled(False)

    def set_time_delay(self):
        time, ok_pressed = QInputDialog.getInt(self, 'Set Time Delay', 'Time Delay:', self.DELAY, 10, 1000, 10)
        if ok_pressed:
            self.DELAY = time

    def start(self):
        # self.start_program.setEnabled(False)
        # # self.stop_program.setEnabled(True)
        # self.add_shortcut.setEnabled(False)
        # self.edit_shortcut.setEnabled(False)
        # self.delete_shortcut.setEnabled(False)
        # self.set_delay.setEnabled(False)

        _time.sleep(2)
        self.run()

    def parse_to_csv(self):
        data = self._cursor.execute("""SELECT * FROM shortcuts""").fetchall()
        headers = ['ID', 'NAME', 'SHORTCUT', 'KEYS']
        with open('shortcuts.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            for i in data:
                writer.writerow(list(i))

    def get_info(self):
        self.info = InfoWidget(self)
        self.info.show()
        self.setEnabled(False)

    def run(self):
        while not _keyboard.is_pressed('esc'):
            for i in self.shortcuts.keys():
                if _keyboard.is_pressed(i):
                    _keyboard.send(self.shortcuts[i.replace(',', '+')])
                    print('Something is pressed')
                _time.sleep(100 / 1000)
            _time.sleep(self.DELAY / 1000)


class AddShortcutWidget(QWidget, Add_UI):
    
    def __init__(self, *args):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Add Shortcut")
        self.main_window = args[0]
        self.connection = sqlite3.connect(args[-1])
        self.cursor = self.connection.cursor()

        self.initUI()

    def initUI(self, *args):
        self.add_button.clicked.connect(self.add_short)
        self.cancel_button.clicked.connect(self.cancel)

    def add_short(self):
        data = (str(self.name_edit.text()), str(self.shortcut_edit.text()), str(self.keys_edit.text()))
        print(data)
        self.cursor.execute("""INSERT 
        INTO shortcuts (name, key_to_press, combination)
        VALUES (?, ?, ?)""", data)
        self.main_window.shortcuts[self.shortcut_edit.text()] = self.keys_edit.text()
        self.connection.commit()

        self.main_window.setEnabled(True)
        self.main_window.database.setDatabaseName(self.main_window.DATABASE_NAME)
        self.main_window.database.open()

        model = QSqlTableModel(self.main_window, self.main_window.database)
        model.setTable('shortcuts')
        model.select()

        self.main_window.shortcuts_view.setModel(model)
        self.hide()

    def cancel(self):
        self.main_window.setEnabled(True)
        self.main_window.database.open()
        self.hide()

    def closeEvent(self, event):
        self.main_window.database.open()
        self.main_window.setEnabled(True)
        super().closeEvent(event)


class DeleteShortcutWidget(QWidget, Delete_UI):

    def __init__(self, *args):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Delete Shortcut")
        self.main_window = args[0]
        self.connection = sqlite3.connect(args[-1])
        self.cursor = self.connection.cursor()
        self.database = QSqlDatabase.addDatabase('QSQLITE')
        self.database.setDatabaseName(args[-1])
        self.database.open()

        self.initUI()
    
    def initUI(self, *args):
        self.delete_button.clicked.connect(self.delete)
        self.cancel_button.clicked.connect(self.cancel)

        model = QSqlTableModel(self, self.database)
        model.setTable('shortcuts')
        model.select()

    def delete(self):
        row = self.shortcuts_list.row()
        print(row)

        self.main_window.database.open()
        self.main_window.setEnabled(True)
        self.main_window.database.setDatabaseName(self.main_window.DATABASE_NAME)
        self.main_window.database.open()

        model = QSqlTableModel(self.main_window, self.main_window.database)
        model.setTable('shortcuts')
        model.select()

        self.main_window.shortcuts_view.setModel(model)
        self.hide()

    def cancel(self):
        self.main_window.database.open()
        self.main_window.setEnabled(True)
        self.hide()
    
    def closeEvent(self, event):
        self.main_window.database.open()
        self.main_window.setEnabled(True)
        super().closeEvent(event)


class InfoWidget(QWidget, Info_UI):

    def __init__(self, *args):
        super().__init__()
        self.setupUi(self)
        self.main_window = args[0]

        self.initUI()

    def initUI(self, *args):
        self.quit_button.clicked.connect(self.return_to_main)

    def return_to_main(self):
        print(0)
        self.main_window.setEnabled(True)
        self.hide()

    def closeEvent(self, event):
        self.main_window.setEnabled(True)
        super().closeEvent(event)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
