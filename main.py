import os
import sys
import glob

from PySide2.QtCore import QUrl, QCoreApplication, QTranslator, QLocale, QFile
from PySide2.QtGui import Qt, QDesktopServices, QFont, QIcon, QPixmap, QFontDatabase
from PySide2.QtWidgets import QMainWindow, QMessageBox, QApplication, QListWidgetItem, QMenu, QAction, QFileDialog, \
    QDialog, QDialogButtonBox

from ui_appvar_text_editor import Ui_MainWindow
from ui_change_font_dialog import Ui_Dialog as Ui_ChangeFontDialog
from ui_select_character import Ui_Dialog as Ui_SelectCharacterDialog

from icon import setupActionsIcons, get_app_icon, get_icon
from const_strings import *

import export


def tr(text: str):  # internal translation
    return QCoreApplication.translate("@default", text, None)


class ChangeFontDialog(QDialog, Ui_ChangeFontDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(get_icon("characters"))

class SelectCharacterDialog(QDialog, Ui_SelectCharacterDialog):
    def __init__(self, parent=None, font=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(get_icon("font_add"))
        tmp_text = r""
        for i_ in range(1, 256):
            tmp_text = tmp_text + chr(i_)  # fill in with characters from 0x01 to 0xFF
        self.plainTextEdit.setPlainText(tmp_text)
        self.plainTextEdit.setFont(font)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        id = QFontDatabase.addApplicationFont(":/font/CEfont.ttf")  # add custom font
        family = QFontDatabase.applicationFontFamilies(id)[0]
        CEfont = QFont(family, 8)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.plainTextEdit.setFont(CEfont)
        setupActionsIcons(self)
        self.saved_path = None
        self.last_opened = None
        self.actionAbout_Qt.triggered.connect(app.aboutQt)
        self.pushButton_2.clicked.connect(self.add_string)
        self.pushButton_3.clicked.connect(self.remove_string)
        self.listWidget.currentItemChanged.connect(self.selection_changed)
        self.plainTextEdit.textChanged.connect(self.editChanged)
        self.pushButton.clicked.connect(lambda: SelectCharacterDialog(self, CEfont).exec_())
        self.actionAbout.triggered.connect(self.about)
        self.update_status_bar()
        self.setWindowIcon(get_app_icon())
        self.plainTextEdit.cursorPositionChanged.connect(self.update_status_bar)
        self.actionView_GitHub_page.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/SiniKra"
                                                                                            "ft/AppvarTextEditor/")))
        self.actionContribute.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/SiniKraft/App"
                                                                                      "varTextEditor/issues/")))
        self.actionNew.triggered.connect(self._new)
        self.actionSave.triggered.connect(self.save)
        self.actionSave_As.triggered.connect(self.save_as)
        self.actionOpen.triggered.connect(self.open)
        self.actionChange_Font.triggered.connect(self.change_font)
        self.actionEnglish.triggered.connect(lambda: self.change_language("en"))
        self.actionExport.triggered.connect(self.export_as_appvar)

        self.menuMore_Actions = QMenu(self)
        self.actionDelete_All = QAction(get_icon("error"), tr("Delete All"), parent=self.menuMore_Actions)
        self.menuMore_Actions.addAction(self.actionDelete_All)
        self.toolButton_4.setMenu(self.menuMore_Actions)
        self.actionDelete_All.triggered.connect(self.listWidget.clear)
        self.load_languages()

    def load_languages(self):
        for directory in glob.glob("translations/*"):
            lang_name = directory.replace("/", "").replace("translations", "").replace("\\", "").replace("(", "")
            # last is security to ensure no arbitrary code is run
            tmp_locale = QLocale(lang_name)
            if not tmp_locale.nativeLanguageName() == "":  # null check
                tmp_icon = QIcon()  # adding all actions to change langs generated on folder content at runtime
                tmp_icon.addPixmap(QPixmap((directory + "/%s_16.png" % lang_name).replace("\\", "/")))
                tmp_icon.addPixmap(QPixmap((directory + "/%s_32.png" % lang_name).replace("\\", "/")))
                tmp_action = QAction(self)
                tmp_action.setObjectName(u"action" + lang_name)
                tmp_action.setText(tmp_locale.languageToString(tmp_locale.language()))
                tmp_action.setIcon(tmp_icon)
                eval('tmp_action.triggered.connect(lambda: win.change_language("%s"))' % lang_name)
                self.menuChange_Language.addAction(tmp_action)
        self.menuChange_Language.addSeparator()
        self.menuChange_Language.addAction(self.actionContribute)

    def add_string(self):
        if self.listWidget.count() != 254:
            __qlistwidgetitem = QListWidgetItem(self.listWidget)
            __qlistwidgetitem.setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            __qlistwidgetitem.setText(tr("New String"))
            __qlistwidgetitem.setSelected(True)
            self.listWidget.setItemSelected(__qlistwidgetitem, True)
            self.listWidget.setCurrentItem(__qlistwidgetitem)
            self.plainTextEdit.setFocus()
            self.selection_changed()

        else:
            showerror(tr("You cannot have more than 254 strings !"),
                      self, tr("Too many strings !"))

    def remove_string(self):
        if self.listWidget.selectedItems():  # check if list is not empty
            _row = self.listWidget.row(self.listWidget.selectedItems()[0])
            self.listWidget.takeItem(_row)  # selecting first element (only one can be selected)
            self.listWidget.setItemSelected(self.listWidget.item(_row - 1), True)
            self.selection_changed()
        else:
            showerror(tr("Select a string first !"), self, tr("No string selected"))

    def update_status_bar(self):
        _str = ""
        if self.listWidget.selectedItems():
            _str = tr(
                "  -  Current string index: {0}  -  Current string length: {1}/254  -  Current char index: {2}").format(
                str(self.listWidget.currentIndex().row()), str(len(self.plainTextEdit.toPlainText())),
                str(self.plainTextEdit.textCursor().position()))
        self.statusBar.showMessage(tr("Number of strings: {0}/254{1}").format(str(self.listWidget.count()), _str))

    def selection_changed(self):
        if self.listWidget.selectedItems():
            try:
                self.plainTextEdit.setPlainText(self.listWidget.currentItem().text())
                self.plainTextEdit.setFocus()
                __qtextcursor = self.plainTextEdit.textCursor()
                __qtextcursor.setPosition(len(self.plainTextEdit.toPlainText()))
                self.plainTextEdit.setTextCursor(__qtextcursor)
            except AttributeError:
                pass
        self.update_status_bar()

    def about(self):
        msg = QMessageBox(self)
        msg.setWindowIcon(get_icon("info"))
        msg.setWindowTitle(tr("About Appvar Text Editor ..."))
        msg.setIcon(QMessageBox.Information)
        msg.setText(tr(about_text))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def editChanged(self):
        if len(self.plainTextEdit.toPlainText()) == 255:
            self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText()[:254])
        if self.listWidget.currentItem() is not None:
            self.listWidget.currentItem().setText(self.plainTextEdit.toPlainText())
        self.update_status_bar()

    def unsaved_change(self):
        pass

    def _new(self):  # clear the window
        self.unsaved_change()
        self.listWidget.clear()
        self.lineEdit.clear()
        self.plainTextEdit.clear()

    def save(self):
        if self.saved_path is not None:
            try:
                export.export_as_ate(self, self.saved_path)
            except Exception as e:
                showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))
        else:
            dg = QFileDialog(self)
            dg.setFileMode(QFileDialog.AnyFile)
            dg.setNameFilter(tr("ATE files (*.ate)"))
            dg.setAcceptMode(QFileDialog.AcceptSave)
            dg.setDefaultSuffix("ate")
            if dg.exec_():
                path = dg.selectedFiles()
                self.last_opened = path[0]
                try:
                    export.export_as_ate(self, path[0])
                    self.saved_path = path[0]
                except Exception as e:
                    showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))

    def save_as(self):
        dg = QFileDialog(self)
        dg.setFileMode(QFileDialog.AnyFile)
        dg.setNameFilter(tr("ATE files (*.ate);;Text files (*.txt);;JSON files (*.json)"))
        dg.setAcceptMode(QFileDialog.AcceptSave)
        dg.setDefaultSuffix("ate")
        if dg.exec_():
            path = dg.selectedFiles()
            self.last_opened = path[0]
            if path[0][-3:] == "ate":  # check extension input by user
                try:
                    export.export_as_ate(self, path[0])
                except Exception as e:
                    showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))
            elif path[0][-3:] == "txt":
                mode = "plain"
                msg = QMessageBox(parent=self)
                msg.setIcon(QMessageBox.Question)
                msg.setText(tr("Choose your mode : comma separated or plain text ?"))
                msg.setWindowTitle(tr("Choose Text Mode"))
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
                msg.button(QMessageBox.Yes).setText(tr("Plain Text"))
                msg.button(QMessageBox.Cancel).setText(tr("Comma Separated Values"))
                msg.exec_()
                if msg.clickedButton() == msg.button(QMessageBox.Cancel):
                    mode = "comma"
                try:
                    export.export_as_txt(self, path[0], mode)
                except Exception as e:
                    showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))
            elif path[0][-3:] == "son":
                try:
                    export.export_as_json(self, path[0])
                except Exception as e:
                    showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))
            else:
                raise NotImplementedError  # if the extension is invalid or unsupported

    def open(self, arg_1=None, _path=None):  # arg_1 is already given by QT system
        if _path is None:
            path = None
            dg = QFileDialog(self)
            dg.setFileMode(QFileDialog.ExistingFile)
            dg.setNameFilter(
                tr("All supported types of files (*.ate; *.txt; *.json);;ATE files (*.ate);;Text files (*.txt);;JSON files (*.json)"))
            dg.setAcceptMode(QFileDialog.AcceptOpen)
            if dg.exec_():
                path = dg.selectedFiles()
                self.last_opened = path[0]
        else:
            path = [_path]
        if path is not None:
            if path[0][-3:] == "ate":
                try:
                    export.import_from_ate(self, path[0])
                except Exception as e:
                    showerror(tr("Failed to open :\n{0}").format(str(e)), self, tr("I/O Error"))
            elif path[0][-3:] == "txt":
                try:
                    export.import_from_txt(self, path[0])
                except Exception as e:
                    showerror(tr("Failed to open :\n{0}").format(str(e)), self, tr("I/O Error"))
            elif path[0][-3:] == "son":
                try:
                    export.import_from_json(self, path[0])
                except Exception as e:
                    showerror(tr("Failed to open :\n{0}").format(str(e)), self, tr("I/O Error"))
            else:
                raise NotImplementedError

    def change_font(self):
        dg = ChangeFontDialog(self)
        dg.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(lambda: self.restore_defaults_font(dg))
        if dg.exec_():
            self.setFont(dg.fontComboBox.currentFont())

    def change_language(self, lang_initial: str):
        try:
            with open("lang", "w", encoding='utf-8') as file:
                file.write(lang_initial)
                file.close()
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowIcon(get_icon("info"))
            msg.setText(tr("Please restart in order to change language."))
            msg.setWindowTitle(tr("Restart needed !"))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except Exception as e:
            showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))

    def restore_defaults_font(self, dg):
        dg.fontComboBox.setFont(QFont("MS Shell Dlg 2"))
        dg.fontComboBox.update()

    def closeEvent(self, event):  # when window closed, save the path of the currently edited file
        if self.last_opened is not None:
            try:
                with open("last_opened", "w", encoding='utf-8') as file:
                    file.write(self.last_opened)
                    file.close()
            except Exception as e:
                showerror(tr("Failed to save :\n{0}").format(str(e)), self, tr("I/O Error"))
        event.accept()

    def ask_to_reopen(self):
        if os.path.isfile("last_opened"):
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Question)
            msg.setText(tr("Do you want to reopen last opened file ?"))
            msg.setWindowTitle(tr("Reopen closed file ?"))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.exec_()
            if msg.clickedButton() == msg.button(QMessageBox.Yes):
                try:
                    with open("last_opened", "r", encoding='utf-8') as file:
                        path_ = file.read()
                        file.close()
                    self.open(None, path_)
                except Exception as e:
                    showerror(tr("Failed to open :\n{0}").format(str(e)), self, tr("I/O Error"))
            else:
                try:
                    os.remove("last_opened")
                except Exception as e:
                    print(e)

    def export_as_appvar(self):
        dg = QFileDialog(self)
        dg.setFileMode(QFileDialog.AnyFile)
        dg.setNameFilter(tr("AppVar files (*.8xv)"))
        dg.setAcceptMode(QFileDialog.AcceptSave)
        dg.setDefaultSuffix("8xv")
        if dg.exec_():
            path = dg.selectedFiles()
            export.export_as_appvar(self, path[0])


def showerror(_msg, _win=None, title=tr("An error occurred")):
    msg = QMessageBox(win)
    msg.setWindowIcon(get_icon("error"))
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Critical)
    msg.setText(_msg)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def load_language(application: QApplication):  # if the 'lang' file exists, try getting QLocale from it
    if os.path.isfile("lang"):
        try:
            with open("lang", "r", encoding='utf-8') as file:
                lang = file.read()
                file.close()
            tmp_locale = QLocale(lang)
            if not tmp_locale.nativeLanguageName() == "":
                for s in ["{0}.qm", "qt_{0}.qm", "qtbase_{0}.qm"]:
                    t = QTranslator(application)
                    t.load(("translations/{0}/" + s).format(lang))
                    application.installTranslator(t)
            else:
                raise Exception("Failed to load lang file")
        except Exception as e:
            print(e)
    else:
        try:
            with open("lang", "w", encoding='utf-8') as file:
                file.write(str(QLocale().system().uiLanguages()[0][:2]))  # First item is preferred language,
                # and get 2 first character of this language e.g. 'en' in 'en_US' (ignoring country-specific locales)
                file.close()
            load_language(application)  # danger: check for recursive calls
        except Exception as e:
            print(e)


if __name__ == "__main__":
    args = sys.argv
    args.append("--enable-smooth-scrolling")  # useful only if using QWebEngineViews
    app = QApplication(args)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # disable useless help button in dialogs
    load_language(app)
    win = MainWindow()
    win.show()
    win.ask_to_reopen()
    sys.exit(app.exec_())
