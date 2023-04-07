import json
import os
import pickle
import struct
import subprocess
import sys

from PySide2.QtWidgets import QListWidgetItem, QMessageBox

from main import MainWindow


def _too_much_strings(mw: "MainWindow"):  # leading '_' mark internal function
    msg = QMessageBox(parent=mw)
    msg.setIcon(QMessageBox.Warning)
    msg.setText("File has too many strings !\nOnly the first 254 ones have been imported !")
    msg.setWindowTitle("Too long file")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def _show_io_error(mw: "MainWindow", text, title):
    msg = QMessageBox(parent=mw)
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def _show_finish_message(mw: "MainWindow", text):
    msg = QMessageBox(parent=mw)
    if text.startswith("[success]"):
        msg.setWindowTitle("Successfully exported !")
        msg.setIcon(QMessageBox.Information)
    else:
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("An error occurred !")
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def export_as_txt(mw: "MainWindow", path, mode):
    string_list = []
    for x in range(0, mw.listWidget.count()):
        string_list.append(mw.listWidget.item(x).text())
    if mode == "plain":
        to_write = ""
        for entry in string_list:
            to_write = to_write + entry + "\n"
        with open(path, 'w', encoding='utf-8') as file:
            file.write(to_write)
    elif mode == "comma":
        to_write = ""
        for entry in string_list:
            to_write = to_write + entry + "﹔"
        with open(path, 'w', encoding="utf-8") as file:
            file.write(to_write)
    else:
        raise NotImplementedError


def export_as_ate(mw: "MainWindow", path):
    string_list = []
    for x in range(0, mw.listWidget.count()):
        string_list.append(mw.listWidget.item(x).text())
    with open(path, 'wb') as file:
        pickle.dump([[mw.lineEdit.text(), mw.lineEdit_2.text()], string_list], file)
        file.close()

def import_from_ate(mw: "MainWindow", path):
    with open(path, 'rb') as loaded_file:
        data = pickle.load(loaded_file)
        loaded_file.close()
    mw.listWidget.clear()
    for string in data[1]:
        if mw.listWidget.count() != 254:
            mw.listWidget.addItem(QListWidgetItem(string[:254]))
        else:
            _too_much_strings(mw)
            break
    mw.listWidget.clearSelection()
    mw.plainTextEdit.clear()
    mw.lineEdit.clear()
    mw.lineEdit.setText(data[0][0])
    mw.lineEdit_2.setText(data[0][1])

def import_from_txt(mw: "MainWindow", path):
    with open(path, 'r', encoding='utf-8') as loaded_file:
        data = loaded_file.readlines()
        loaded_file.close()
    mw.listWidget.clear()
    for string in data:
        if string !="\n":
            if mw.listWidget.count() != 254:
                mw.listWidget.addItem(QListWidgetItem(string.replace("\n", "")[:254]))
            else:
                _too_much_strings(mw)
                break
    mw.lineEdit.clear()
    mw.listWidget.clearSelection()
    mw.plainTextEdit.clear()


def export_as_json(mw: "MainWindow", path):
    string_list = []
    for x in range(0, mw.listWidget.count()):
        string_list.append(mw.listWidget.item(x).text())
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(string_list, file, indent=4)


def import_from_json(mw: "MainWindow", path):
    with open(path, 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
    mw.listWidget.clear()
    for string in data:
        if string != "\n":
            if mw.listWidget.count() != 254:
                mw.listWidget.addItem(QListWidgetItem(string.replace("\n", "")[:254]))
            else:
                _too_much_strings(mw)
                break
    mw.lineEdit.clear()
    mw.listWidget.clearSelection()
    mw.plainTextEdit.clear()

def export_as_appvar(mw: "MainWindow", path):
    # COMMAND : convbin -l 3 -r -n VAR_NAME -j bin -k 8xv -i INPUT -o OUTPUT
    header_list = [b'\x00']  # this first byte will be edited later
    str_list = []
    # For an explanation on how the following works, please refer to the PNG 'ATE Explained.png'
    if mw.lineEdit_2.text() == "":
        _show_finish_message(mw, "Please input a name")  # small security check
    for x in range(0, mw.listWidget.count()):
        line_text = mw.listWidget.item(x).text()
        header_list.append(struct.pack("B", len(line_text) + 1))  # B = Unsigned char
        str_list.append(bytes(line_text + chr(0), "cp1252"))
    header_list[0] = struct.pack("B", len(header_list))  # editing first byte containing header length
    final_bytes = bytes(mw.lineEdit.text(), "cp1252")  # adding header string first
    for byte_group in (header_list + str_list):
        final_bytes = final_bytes + byte_group  # finally build the file content by converting list of bytes to bytes
    try:
        with open(path + ".bin.tmp", "wb") as file:  # writing bin file to be converted by convbin utility to 8xv
            file.write(final_bytes)
            file.close()
        conv_bin_path = "convbin-lin"
        if sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys":
            conv_bin_path = "convbin.exe"
        elif sys.platform == "darwin":
            conv_bin_path = "convbin-darwin"
        _show_finish_message(mw, subprocess.check_output([
            conv_bin_path, '-l', '3', '-r', '-n', mw.lineEdit_2.text(), '-j', 'bin', '-k', '8xv', '-i',
            path + ".bin.tmp", '-o', path]).decode())
        os.remove(path + ".bin.tmp")

    except Exception as e:
        _show_io_error(mw, "Failed to export !\n%s" % str(e), "I/O Error")

