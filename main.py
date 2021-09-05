from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from random import randint


class GameBlock(QLabel):
    def __init__(self, x, y):
        super(GameBlock, self).__init__()
        self.is_mine = False
        self.is_opened = False
        self.is_flag = False
        self.setFixedSize(20, 20)
        self.normal_style = u"QWidget {background-color: rgb(199, 199, 199);} " \
                            u"QWidget:hover {background-color: rgb(150, 150, 150);}"
        self.mine_style = u"QWidget {background-color: red;}"
        self.flag_style = u"QWidget {background-color: blue;}"
        self.setStyleSheet(self.normal_style)
        self.x = x
        self.y = y
        self.reset()

    def reset(self):
        self.is_mine = False
        self.is_opened = False
        self.is_flag = False
        self.setStyleSheet(self.normal_style)
        self.setText('')
        self.update()

    def mouseReleaseEvent(self, ev):
        if self.parentWidget().GAME_OVER:
            self.parentWidget().reset_map()
            return
        elif self.parentWidget().FIRST:
            self.parentWidget().add_mines(self.x, self.y)
        if ev.button() == Qt.RightButton and not self.is_opened:
            self.toggle_flag()
            self.parentWidget().check_finish()
        elif ev.button() == Qt.LeftButton and not self.is_flag and not self.is_opened:
            self.bl_click()
            self.parentWidget().check_finish()
        elif ev.button() == Qt.MiddleButton and self.is_opened:
            self.mid_click()

    def mid_click(self):
        sur = self.parentWidget().get_surround(self.x, self.y)
        if sur[0] == sur[2]:
            self.parentWidget().mid_open(self.x, self.y)

    def toggle_flag(self):
        if self.is_flag:
            self.is_flag = False
            self.setStyleSheet(self.normal_style)
        else:
            self.is_flag = True
            self.setStyleSheet(self.flag_style)
        self.update()

    def bl_click(self):
        self.is_opened = True
        if self.is_mine is True:
            self.setStyleSheet(self.mine_style)
            self.parentWidget().show_mines()
            self.parentWidget().GAME_OVER = True
            QMessageBox.information(self.parentWidget(), "Игра", "Вы проиграли!")
        else:
            self.set_open()
            self.parentWidget().open_near(self.x, self.y)

    def set_open(self):
        mines = self.parentWidget().get_surround(self.x, self.y)[0]
        if mines != 0:
            self.is_opened = True
            self.setText(str(mines))
        self.setStyleSheet(u"QWidget {background-color: white;}")


class GameField(QWidget):
    def __init__(self, x, y, mines):
        super(GameField, self).__init__()
        self.setWindowTitle('MineSweeper')
        self.grid = QGridLayout(self)
        self.grid.setSpacing(3)
        self.size_x = x
        self.size_y = y
        self.GAME_OVER = False
        self.FIRST = True
        self.mines_count = int(self.size_x * self.size_y * (mines/100))
        self.init_map()

    def init_map(self):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                aw = GameBlock(x, y)
                self.grid.addWidget(aw, x, y)

    def reset_map(self):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                self.grid.itemAtPosition(x, y).widget().reset()
        self.GAME_OVER = False
        self.FIRST = True

    def show_mines(self):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                v = self.grid.itemAtPosition(x, y).widget()
                if v.is_mine:
                    v.setStyleSheet(v.mine_style)

    def check_finish(self):
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                v = self.grid.itemAtPosition(x, y).widget()
                if v.is_mine is True and v.is_flag is False:
                    return
        QMessageBox.information(self, "Игра", "Вы выиграли!")
        self.GAME_OVER = True

    def add_mines(self, x, y):
        mines = set()
        while len(mines) < self.mines_count:
            mines.add((randint(0, self.size_x-1), randint(0, self.size_y-1)))
            if (x, y) in mines:
                mines.remove((x, y))
        for xi, yi in mines:
            self.grid.itemAtPosition(xi, yi).widget().is_mine = True

    def get_surround(self, x, y):
        mines_around = 0
        flags_around = 0
        surround = []
        full_surround = []
        for xi in range(max(0, x-1), min(x+2, self.size_x)):
            for yi in range(max(0, y - 1), min(y + 2, self.size_y)):
                full_surround.append((xi, yi))
                if not (xi == x and yi == y) and self.grid.itemAtPosition(xi, yi).widget().is_mine is True:
                    mines_around += 1
                if not (xi == x and yi == y) and self.grid.itemAtPosition(xi, yi).widget().is_flag is True:
                    flags_around += 1
                if self.grid.itemAtPosition(xi, yi).widget().is_mine is False:
                    surround.append((xi, yi))
        return mines_around, surround, flags_around, full_surround

    def open_near(self, x, y):
        empty = []
        if self.FIRST is True:
            empty.append((x, y))
            self.FIRST = False
        for xi, yi in self.get_surround(x, y)[1]:
            if not (xi == x and yi == y) and self.get_surround(xi, yi)[0] == 0 \
                    and self.grid.itemAtPosition(xi, yi).widget().is_opened is False:
                empty.append((xi, yi))
        if empty:
            self.open_sur(empty)

    def open_sur(self, to_open):
        for xi, yi in to_open:
            self.grid.itemAtPosition(xi, yi).widget().is_opened = True
            for xj, yj in self.get_surround(xi, yi)[1]:
                if self.get_surround(xj, yj)[0] == 0:
                    self.open_near(xj, yj)
                self.grid.itemAtPosition(xj, yj).widget().set_open()

    def mid_open(self, x, y):
        for xi, yi in self.get_surround(x, y)[3]:
            if self.grid.itemAtPosition(xi, yi).widget().is_opened is False \
                    and self.grid.itemAtPosition(xi, yi).widget().is_flag is False:
                self.grid.itemAtPosition(xi, yi).widget().bl_click()


class StartWindow(QWidget):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.setWindowTitle('MineSweeper')
        self.resize(160, 198)
        self.gridLayout_3 = QGridLayout(self)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.spinBox = QSpinBox(self)
        self.spinBox.setObjectName(u"spinBox")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.spinBox, 1, 0, 1, 1)
        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setFamily(u"Arial")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(Qt.LeftToRight)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.spinBox_2 = QSpinBox(self)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setEnabled(True)
        sizePolicy.setHeightForWidth(self.spinBox_2.sizePolicy().hasHeightForWidth())
        self.spinBox_2.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.spinBox_2, 1, 2, 1, 1)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(2, 2)
        self.gridLayout.setRowMinimumHeight(1, 15)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(self)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 2)
        self.spinBox_3 = QSpinBox(self)
        self.spinBox_3.setObjectName(u"spinBox_3")
        sizePolicy.setHeightForWidth(self.spinBox_3.sizePolicy().hasHeightForWidth())
        self.spinBox_3.setSizePolicy(sizePolicy)
        self.gridLayout_2.addWidget(self.spinBox_3, 1, 0, 1, 1)
        self.label_4 = QLabel(self)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)
        self.gridLayout_2.setRowMinimumHeight(1, 15)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.pushButton = QPushButton(self)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        self.gridLayout_3.addWidget(self.pushButton, 1, 0, 1, 1)
        self.label_2.setText(QCoreApplication.translate("Form", u"\u0445", None))
        self.label.setText(
            QCoreApplication.translate("Form", u"\u0420\u0430\u0437\u043c\u0435\u0440 \u043f\u043e\u043b\u044f:", None))
        self.label_3.setText(QCoreApplication.translate("Form",
                                                        u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043c\u0438\u043d:",
                                                        None))
        self.label_4.setText(QCoreApplication.translate("Form", u"%", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u0421\u0442\u0430\u0440\u0442", None))
        self.spinBox.setValue(9)
        self.spinBox_2.setValue(9)
        self.spinBox_3.setValue(20)
        self.connect(self.pushButton, SIGNAL('clicked()'), self, SLOT('start_saper()'))

    def start_saper(self):
        x = self.spinBox.value()
        y = self.spinBox_2.value()
        mines = self.spinBox_3.value()
        global gf
        gf = GameField(x, y, mines)
        gf.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication([])
    w = StartWindow()
    w.show()
    app.exec_()
