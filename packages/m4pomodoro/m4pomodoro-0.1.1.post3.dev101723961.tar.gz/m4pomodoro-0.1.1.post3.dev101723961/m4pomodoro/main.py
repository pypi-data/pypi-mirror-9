#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import signal
import sqlite3
import time
# import datetime
import argparse
# import configparser
# import logging
import pkg_resources
from gi.repository import Notify
from subprocess import call
from enum import Enum
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtNetwork


class Timer(QtCore.QObject):
    timeout = QtCore.pyqtSignal()
    on_tick = QtCore.pyqtSignal()

    def __init__(self, t, parent):
        super(Timer, self).__init__(parent)
        self.t_timeout = t
        self.t_elapsed = 0
        self.timer = QtCore.QTimer(parent)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

    def start(self, reset):
        if reset:
            self.t_elapsed = 0

        self.timer.start()

    def stop(self):
        self.timer.stop()

    def elapsed(self):
        return self.t_elapsed

    def tick(self):
        self.t_elapsed = self.t_elapsed + 1
        self.on_tick.emit()
        if self.t_elapsed >= self.t_timeout:
            self.timer.stop()
            self.timeout.emit()


class Status(Enum):
    idle = 1
    work = 2
    pause = 3
    wbreak = 4


class StatusManager(QtCore.QObject):
    statusChange = QtCore.pyqtSignal()
    success = QtCore.pyqtSignal()
    failure = QtCore.pyqtSignal()
    start = QtCore.pyqtSignal()
    tick = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(StatusManager, self).__init__(parent)
        self.parent = parent
        self.t_work = 25*60
        self.t_break = 5*60
        self.t_pause = 60
        self.status = Status.idle
        self.wtimer = Timer(self.t_work, parent)
        self.wtimer.timeout.connect(lambda: self.timer_trigger("work"))
        self.wtimer.on_tick.connect(self.tick)

        self.btimer = Timer(self.t_break, parent)
        self.btimer.timeout.connect(lambda: self.timer_trigger("break"))
        self.btimer.on_tick.connect(self.tick)

        self.ptimer = Timer(self.t_pause, parent)
        self.ptimer.timeout.connect(lambda: self.timer_trigger("pause"))
        self.ptimer.on_tick.connect(self.tick)

    def trigger(self):
        if self.status == Status.idle:
            self.startWork()
        elif self.status == Status.work:
            self.interruptWork()
        elif self.status == Status.pause:
            self.continueWork()
        elif self.status == Status.wbreak:
            self.finishWork()

    def timer_trigger(self, ttype):
        # print("timer: ", ttype)
        if ttype == "work":
            self.finishWork()
        elif ttype == "break":
            self.finishBreak()
        elif ttype == "pause":
            self.timoutPause()

    def startWork(self):
        rv = QtGui.QInputDialog.getText(
            self.parent,
            "m4pmodoro",
            "Work:",
            QtGui.QLineEdit.Normal)
        if rv[1] is True and rv[0] is not "":
            self.worktext = rv[0]
            self.status = Status.work
            self.wtimer.start(True)
            self.start.emit()
            self.statusChange.emit()

    def interruptWork(self):
        self.wtimer.stop()
        self.ptimer.start(True)
        self.status = Status.pause
        self.statusChange.emit()

    def timoutPause(self):
        self.ptimer.stop()
        self.status = Status.idle
        self.failure.emit()
        self.statusChange.emit()

    def continueWork(self):
        self.ptimer.stop()
        self.wtimer.start(False)
        self.status = Status.work
        self.statusChange.emit()

    def finishWork(self):
        self.status = Status.wbreak
        self.btimer.start(True)
        self.success.emit()
        self.statusChange.emit()

    def finishBreak(self):
        self.status = Status.idle
        self.statusChange.emit()

    def statusInfo(self):
        elapsed = 0
        m_time = 0
        if self.status == Status.work:
            elapsed = self.wtimer.elapsed()
            m_time = self.t_work
        elif self.status == Status.pause:
            elapsed = self.ptimer.elapsed()
            m_time = self.t_pause
        elif self.status == Status.wbreak:
            elapsed = self.btimer.elapsed()
            m_time = self.t_break

        return {"status": self.status,
                "elapsed": elapsed,
                "max":  m_time}


class DB:
    def __init__(self):
        conn = self.connection()
        sql = '''create table if not exists poms
            (time int, work text)'''
        conn.execute(sql)
        conn.commit()
        conn.close()

    def add_success(self, work=""):
        conn = self.connection()
        conn.execute("INSERT INTO poms VALUES(:time, :work)",
                     {"time": time.time(), "work": work})
        conn.commit()
        conn.close()

    def get_works(self):
        conn = self.connection()
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM poms")

    def connection(self):
        return sqlite3.connect('data.db')


class Pomodoro(QtGui.QWidget):
    def __init__(self):
        super(Pomodoro, self).__init__()
        # self.db = DB()
        self.sm = StatusManager(self)
        self.initUI()
        self.status_changed()
        self.tray.show()

    def initUI(self):
        Notify.init("m4pomodoro")

        tomate_green = pkg_resources.resource_filename(
            __name__, "data/tomate_green.svg")
        tomate_blue = pkg_resources.resource_filename(
            __name__, "data/tomate_blue.svg")
        tomate_red = pkg_resources.resource_filename(
            __name__, "data/tomate_red.svg")
        tomate_yellow = pkg_resources.resource_filename(
            __name__, "data/tomate_yellow.svg")
        self.green_tray = QtGui.QIcon(tomate_green)
        self.blue_tray = QtGui.QIcon(tomate_blue)
        self.red_tray = QtGui.QIcon(tomate_red)
        self.yellow_tray = QtGui.QIcon(tomate_yellow)

        # self.resize(250, 150)
        self.setWindowTitle("m4Pomodoro")

        self.label = QtGui.QLabel(self)
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setFormat("%v")

        table = QtGui.QTableWidget(0, 2, self)
        table.setHorizontalHeaderLabels(["Date", "Work"])

        # ws = self.db.get_works()
        # for row in ws:
        #     table.insertRow(0)
        #     dt = datetime.datetime.fromtimestamp(int(row['time']))
        #     date = dt.strftime("%H:%M %d/%m/%Y")
        #     item = QtGui.QTableWidgetItem()
        #     item.setText(date)
        #     table.setItem(0, 0, item)

        #     work = row['work']
        #     item = QtGui.QTableWidgetItem()
        #     item.setText(work)
        #     table.setItem(0, 1, item)

        grid = QtGui.QGridLayout()
        # button = QtGui.QPushButton("Button")
        grid.addWidget(self.label, 0, 0)
        grid.addWidget(self.pbar, 0, 1)
        grid.addWidget(table, 1, 1)

        self.setLayout(grid)
        # grid.addWidget(self.pbar,1,1)
        eAction = QtGui.QAction('&Exit', self)
        eAction.triggered.connect(QtGui.QApplication.exit)
        traymenu = QtGui.QMenu(self)
        traymenu.addAction(eAction)

        self.tray = QtGui.QSystemTrayIcon(self)
        self.tray.setContextMenu(traymenu)
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        self.connect(self.tray, QtCore.SIGNAL(traySignal), self.mouse_signal)

        self.sm.statusChange.connect(self.status_changed)
        self.sm.start.connect(self.work_started)
        self.sm.success.connect(self.work_success)
        self.sm.failure.connect(self.work_failed)
        self.sm.tick.connect(self.on_tick)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def send_notification(self, title, descr):
        n = Notify.Notification.new(title, descr)
        n.show()

    def mouse_signal(self, reason):
        if reason == 3:         # LeftClick
            self.setVisible(not self.isVisible())
        elif reason == 4:       # Middle
            self.sm.trigger()

    def work_started(self):
        call(["hamster", "start", self.sm.worktext])
        self.send_notification(self.sm.worktext, "started")
        # print("work_started")

    def work_success(self):
        call(["hamster", "stop", self.sm.worktext])
        self.send_notification(self.sm.worktext, "pomodoro finished")
        # self.db.add_success()
        # print("work_success")
        self.show()

    def work_failed(self):
        # print("work_failed")
        call(["hamster", "stop", self.sm.worktext])
        self.send_notification(self.sm.worktext, "failed pomodoro")

    def status_changed(self):
        if self.sm.status == Status.idle:
            self.tray.setIcon(self.green_tray)
        elif self.sm.status == Status.work:
            self.tray.setIcon(self.red_tray)
        elif self.sm.status == Status.pause:
            self.tray.setIcon(self.yellow_tray)
        elif self.sm.status == Status.wbreak:
            self.tray.setIcon(self.blue_tray)

        self.on_tick()

    def statusInfo(self):
        return self.sm.statusInfo()

    def on_tick(self):
        info = self.sm.statusInfo()

        if info['status'] == Status.pause:
            self.pbar.setInvertedAppearance(True)
        else:
            self.pbar.setInvertedAppearance(False)

        self.pbar.setRange(0, info['max'])
        self.pbar.setValue(info['elapsed'])
        self.label.setText("{status}".format(status=info['status']))
        self.tray.setToolTip("{status}:{elapsed}/{max}".format(
            elapsed=info['elapsed'],
            max=info['max'],
            status=info['status']))


class SingleApp(QtGui.QApplication):
    def getStatus(self, status_return, cmd=""):
        self.status_return = status_return
        self.status_send_cmd = cmd
        self.m_socket = QtNetwork.QLocalSocket()
        self.m_socket.connected.connect(self.getStatusInfo)
        self.m_socket.error.connect(self.failedStatusInfo)
        self.m_socket.connectToServer("m4pomodoro")

    def getStatusInfo(self):
        if not self.status_send_cmd == "":
            self.m_socket.write(self.status_send_cmd)
            self.m_socket.write('\n')

        self.m_socket.write("getStatus")
        if self.m_socket.waitForReadyRead(3000):
            f = self.m_socket.readLine()
            self.status_return.print_status(f.data())
        else:
            self.status_return.print_status("timeout")

        self.quit

    def failedStatusInfo(self):
        # print(self.m_socket.errorString())
        self.status_return.print_status("not_running")

    def singleStart(self):
        self.m_socket = QtNetwork.QLocalSocket()
        self.m_socket.connected.connect(self.connectToExistingApp)
        self.m_socket.error.connect(self.startApplication)
        self.m_socket.connectToServer("m4pomodoro")

    def startApplication(self):
        self.m_server = QtNetwork.QLocalServer()
        self.m_server.removeServer("m4pomodoro")
        if self.m_server.listen("m4pomodoro"):
            self.m_server.newConnection.connect(self.getNewConnection)
            self.pom = Pomodoro()
        else:
            # print("failed server")
            self.quit

    def connectToExistingApp(self):
        print("Instance already running.")
        self.m_socket.write("show")
        self.m_socket.bytesWritten.connect(self.quit)

    def getNewConnection(self):
        self.new_socket = self.m_server.nextPendingConnection()
        self.new_socket.readyRead.connect(self.readSocket)

    def readSocket(self):
        f2 = self.new_socket.readLine().data()
        f = f2.strip().decode("utf-8")
        if f == "show":
            self.pom.setVisible(True)
        elif f == "getStatus":
            info = self.pom.statusInfo()
            self.new_socket.write("{status},{elapsed},{max}".format(
                status=info["status"],
                elapsed=info["elapsed"],
                max=info["max"]))
        elif f == "BUTTON1":
            self.pom.mouse_signal(3)
        elif f == "BUTTON2":
            self.pom.mouse_signal(4)
        elif f == "BUTTON3":
            self.pom.mouse_signal(1)


class StatusReturn:
    def __init__(self, f):
        self.format = "i3blocks"

    def print_status(self, data):
        self.i3blocks(data)

    def i3blocks(self, data):
        if data == "not_running" or data == "timeout":
            exit(0)

        color = "#0000FF"
        full_text = "whhhh"
        code = 0

        d = data.decode("utf-8").split(',')
        status = d[0]
        elapsed = int(d[1])
        max = int(d[2])
        left = max - elapsed
        m, s = divmod(left, 60)

        if status == "Status.work":
            full_text = "WORKING ( {m}:{s} left )".format(m=m, s=s)
            color = "#FF6600"

        elif status == "Status.wbreak":
            full_text = "BREAK ( {m}:{s} left )".format(m=m, s=s)
            code = 33

        elif status == "Status.pause":
            full_text = "PAUSE ( {m}:{s} left )".format(m=m, s=s)
            code = 33

        elif status == "Status.idle":
            full_text = "CHILL"
            color = "009900"

        print(full_text)
        print("")
        print(color)
        exit(code)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description='Pomodoro Application')
    parser.add_argument('--action', default="start", required=False)
    args = parser.parse_args()

    app = SingleApp(sys.argv)

    if args.action == "i3blocks":
        cmd = ""
        button = os.environ.get("BLOCK_BUTTON")
        if button is not None and button != "":
            cmd = "BUTTON{button}".format(button=button)

        sr = StatusReturn("i3blocks")
        app.getStatus(sr, cmd)
        return

    # config = configparser.ConfigParser()
    # config.read("~/.config/m4pomodoro.conf")

    app.singleStart()
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
