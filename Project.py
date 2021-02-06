import sys
import subprocess
import PyQt5
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QApplication, QTextBrowser, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QColorDialog
import sqlite3

ADRESS = open(r'adress.txt', encoding='utf-8').read().rstrip()
BUTTON_STYLE = open(r'button_style.txt').read()
TEXT_BROWSER_STYLE = open(r'text_browser_style.txt').read()


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    PyQt5.QtWidgets.QMessageBox.critical(None, 'Error', text)
    quit()


sys.excepthook = log_uncaught_exceptions


class Window2(QWidget):
    def __init__(self, action, k=0, matter='', par='', qi=0.0):
        super().__init__()
        self.action = action
        self.k = k
        self.matter = matter
        self.par = par
        self.qi = qi
        self.initUI()

    def initUI(self):
        global ADRESS, BUTTON_STYLE, TEXT_BROWSER_STYLE
        self.con = sqlite3.connect(ADRESS)
        self.cur = self.con.cursor()

        self.setGeometry(50, 50, 500, 320)
        self.setStyleSheet('background-color: #00fa9a')

        if self.action == 'report_matter':
            if self.par == 'Код':
                result = self.cur.execute(f'''SELECT * FROM substances
                                              WHERE code = {int(self.matter)}''').fetchall()
            else:
                result = self.cur.execute(f"""SELECT code,
       name,
       tons_year_norm,
       tons_year_fact,
       rate,
       class FROM substances
                                              WHERE name = '{self.matter}'""").fetchall()
            if result:
                self.text = f'''{result[0][0]}: {result[0][1]} 
Нормативный объём выбросов: {result[0][2]} т/год
Фактический объём выбросов: {result[0][3]} т/год
Ставка платы за превышение норматива: {result[0][4]}
Класс: {result[0][5]}\n'''
                res = self.cur.execute(f'''SELECT class_description FROM classes
                                       WHERE num = {result[0][5]}''').fetchall()
                self.text += f'Описание класса: {res[0][0]}'

                self.setWindowTitle(f'Отчёт по веществу {result[0][1]}')
            else:
                self.text = 'Такого вещества в справочнике нет. Возможно, Вы перепутали справочники или ошиблись в ' \
                            'названии или коде вещества. Проверьте правильность введённых данных и повторите попытку.'
                self.setWindowTitle('Вещество не найдено!')
                self.setStyleSheet('background-color: #ff2e2e')

            self.text_browser = QTextBrowser(self)
            self.text_browser.setStyleSheet(TEXT_BROWSER_STYLE)
            self.text_browser.setFontPointSize(11)
            self.text_browser.setPlainText(self.text)
            self.text_browser.resize(400, 200)
            self.text_browser.move(10, 100)

            self.b_back = QPushButton(self)
            self.b_back.setStyleSheet(BUTTON_STYLE)
            self.b_back.setText('Назад')
            self.b_back.resize(150, 50)
            self.b_back.move(20, 20)
            self.b_back.clicked.connect(self.back)

        elif self.action == 'report_payment':
            self.setGeometry(50, 50, 500, 350)
            self.setWindowTitle('Отчёт по оплате')
            self.setStyleSheet('background-color: #00fa9a')

            result = self.cur.execute('''SELECT * FROM substances''').fetchall()
            self.text = ''
            for i, matter in enumerate(result):
                self.text += f'''{matter[0]}: {matter[1]}
Нормативный объём выбросов: {matter[2]} т/год
Фактический объём выбросов: {matter[3]} т/год\n'''
                if matter[3] > matter[2]:
                    self.text += f'''К оплате: {(matter[2] * matter[4] * self.qi) + ((matter[3] - matter[2]) * matter[4] * self.qi * 5)} руб.
Норматив превышен на {matter[3] - matter[2]} т/год\n\n'''
                else:
                    self.text += f'''К оплате: {matter[2] * matter[4] * self.qi} руб.
Норматив не превышен\n\n'''

            self.text_browser = QTextBrowser(self)
            self.text_browser.setStyleSheet(TEXT_BROWSER_STYLE)
            self.text_browser.setFontPointSize(11)
            self.text_browser.setPlainText(self.text)
            self.text_browser.resize(400, 200)
            self.text_browser.move(10, 100)

            self.b_back = QPushButton(self)
            self.b_back.setStyleSheet(BUTTON_STYLE)
            self.b_back.setText('Назад')
            self.b_back.resize(150, 50)
            self.b_back.move(20, 20)
            self.b_back.clicked.connect(self.back)


        elif self.action == 'klass':
            self.setGeometry(50, 50, 500, 450)
            self.setWindowTitle(f'Все вещества {self.k} класса опасности')
            self.setStyleSheet('background-color: #00fa9a')

            result = self.cur.execute(f'''SELECT code, name FROM substances 
                                          WHERE class = {int(self.k)}''').fetchall()
            res = self.cur.execute(f'''SELECT class_description FROM classes 
                                       WHERE num = {int(self.k)}''').fetchall()

            self.text = f'{res[0][0]}\nВещества {self.k} класса опасности:\n'
            for i in result:
                self.text += f'{i[0]}: {i[1]}; \n'

            self.text_browser = QTextBrowser(self)
            self.text_browser.setStyleSheet(TEXT_BROWSER_STYLE)
            self.text_browser.setFontPointSize(11)
            self.text_browser.setPlainText(self.text)
            self.text_browser.resize(300, 300)
            self.text_browser.move(10, 100)

            self.b_back = QPushButton(self)
            self.b_back.setStyleSheet(BUTTON_STYLE)
            self.b_back.setText('Назад')
            self.b_back.resize(150, 50)
            self.b_back.move(20, 20)
            self.b_back.clicked.connect(self.back)

        elif self.action == 'statistics':
            self.setGeometry(50, 50, 500, 430)
            self.setWindowTitle('Статистика')
            self.setStyleSheet('background-color: #00fa9a')

            result = self.cur.execute(
                f'''SELECT code, name, tons_year_norm, tons_year_fact FROM substances''').fetchall()

            count_matters, count_above_li = 0, []
            for matter in result:
                if matter[3] > matter[2]:
                    count_above_li.append(f'{matter[0]}: {matter[1]};\n')
                count_matters += 1

            self.text = f'''Норматив превышен {len(count_above_li)} раз из {count_matters}
Вещества с превышающими нормативы выбросами:\n {''.join(count_above_li)}'''

            self.text_browser = QTextBrowser(self)
            self.text_browser.setStyleSheet(TEXT_BROWSER_STYLE)
            self.text_browser.setFontPointSize(11)
            self.text_browser.setPlainText(self.text)
            self.text_browser.resize(400, 300)
            self.text_browser.move(10, 100)

            self.b_back = QPushButton(self)
            self.b_back.setStyleSheet(BUTTON_STYLE)
            self.b_back.setText('Назад')
            self.b_back.resize(150, 50)
            self.b_back.move(20, 20)
            self.b_back.clicked.connect(self.back)

    def back(self):
        win = Window()
        win.show()
        self.close()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global ADRESS, BUTTON_STYLE
        self.setGeometry(50, 50, 650, 400)
        self.setWindowTitle('Выберите действие')
        self.setStyleSheet('background-color: #ffffff')

        if ADRESS == '':
            self.choose_database()

        self.database_label = QLabel(self)
        self.database_label.setText(f'Подключённая база данных: {ADRESS}')
        self.database_label.move(20, 30)

        self.b_choose_database = QPushButton(self)
        self.b_choose_database.setStyleSheet('background-color: #f0f0f0')
        self.b_choose_database.resize(100, 20)
        self.b_choose_database.move(25, 50)
        self.b_choose_database.setStyleSheet('font-style:italic')
        self.b_choose_database.setText('Изменить...')
        self.b_choose_database.clicked.connect(self.choose_database)

        self.b_report_matter = QPushButton(self)
        self.b_report_matter.setStyleSheet(BUTTON_STYLE)
        self.b_report_matter.resize(200, 50)
        self.b_report_matter.move(100, 100)
        self.b_report_matter.setText('Отчёт по веществу')
        self.b_report_matter.clicked.connect(self.report_matter)

        self.b_report_payment = QPushButton(self)
        self.b_report_payment.setStyleSheet(BUTTON_STYLE)
        self.b_report_payment.resize(200, 50)
        self.b_report_payment.move(350, 100)
        self.b_report_payment.setText('Отчёт по плате')
        self.b_report_payment.clicked.connect(self.report_payment)

        self.b_klass = QPushButton(self)
        self.b_klass.setStyleSheet(BUTTON_STYLE)
        self.b_klass.resize(200, 50)
        self.b_klass.move(100, 180)
        self.b_klass.setText('Все вещества ... класса опасности')
        self.b_klass.clicked.connect(self.klass)

        self.b_statistics = QPushButton(self)
        self.b_statistics.setStyleSheet(BUTTON_STYLE)
        self.b_statistics.resize(200, 50)
        self.b_statistics.move(350, 180)
        self.b_statistics.setText('Статистика')
        self.b_statistics.clicked.connect(self.statistics)

        self.b_set_color = QPushButton(self)
        self.b_set_color.setStyleSheet(BUTTON_STYLE)
        self.b_set_color.resize(200, 50)
        self.b_set_color.move(100, 260)
        self.b_set_color.setText('Изменить цвет кнопок')
        self.b_set_color.clicked.connect(self.set_color)

        self.b_clos = QPushButton(self)
        self.b_clos.setStyleSheet(BUTTON_STYLE)
        self.b_clos.resize(200, 50)
        self.b_clos.move(350, 260)
        self.b_clos.setText('Выход')
        self.b_clos.clicked.connect(self.close)

    def choose_database(self):
        global ADRESS
        self.get_adress = QFileDialog.getOpenFileName(self, 'Выберите базу данных(справочник)', '',
                                                      'База данных(*.db')[0]
        with open(r'adress.txt', 'w', encoding='utf-8') as f:
            print(f'{self.get_adress.rstrip()}', file=f)
        ADRESS = open(r'adress.txt', encoding='utf-8').read()
        self.close()
        subprocess.call("python" + " Project.py", shell=True)

    def report_matter(self):
        par, okBtnPressed2 = QInputDialog.getItem(self, 'Выберите способ ввода',
                                                  'Выберите параметр поиска',
                                                  ('Название', 'Код'),
                                                  1, False)
        if okBtnPressed2:
            i, okBtnPressed = QInputDialog.getText(self, 'Выберите вещество',
                                                   f'Введите {par.lower()} вещества, как в таблице')
            if okBtnPressed:
                self.win1 = Window2('report_matter', matter=i, par=par)
                self.win1.show()

    def report_payment(self):
        i, okBtnPressed = QInputDialog.getText(self, 'Введите коэффициент инфляции',
                                               'Формат ввода: x.xx', )
        if i:
            if okBtnPressed:
                self.win1 = Window2('report_payment', qi=float(i))
                self.win1.show()

    def klass(self):
        i, okBtnPressed = QInputDialog.getItem(self, 'Выберите класс опасности',
                                               ' ',
                                               ('1', '2', '3', '4'),
                                               1, False)
        if okBtnPressed:
            self.win1 = Window2('klass', i)
            self.win1.show()

    def statistics(self):
        self.win1 = Window2('statistics')
        self.win1.show()

    def set_color(self):
        global BUTTON_STYLE
        i, okBtnPressed = QInputDialog.getItem(self, 'Настройки цвета',
                                               '',
                                               ('Выбрать цвет...', 'Цвет по умолчанию'),
                                               1, False)
        if okBtnPressed:
            if i == 'Выбрать цвет...':
                color = QColorDialog.getColor()
            else:
                color = QColor()
                color.setNamedColor('#84e8e8')
            with open(r'button_style.txt', 'w') as f:
                print(f'background-color: {color.name()}', file=f)
            BUTTON_STYLE = open(r'button_style.txt').read()
            self.close()
            subprocess.call("python" + " Project.py", shell=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
