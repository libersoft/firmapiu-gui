#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2015 Libersoft <info[at]libersoft[dot]it”

# This file is part of firmapiu-gui.
#
#    firmapiu-gui is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    firmapiu-gui is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with firmapiu-gui.  If not, see <http://www.gnu.org/licenses/>.


import sys
from PyQt5.Qt import QDialog
from PyQt5.Qt import QMessageBox
from PyQt5.Qt import QWidget
from PyQt5.Qt import QTabWidget
from PyQt5.Qt import QLabel
from PyQt5.Qt import QLineEdit
from PyQt5.Qt import QRegExpValidator
from PyQt5.Qt import QRegExp
from PyQt5.Qt import QApplication
from PyQt5.Qt import QDialogButtonBox
from PyQt5.Qt import QVBoxLayout
from PyQt5.Qt import QLocale
from PyQt5.Qt import Qt

# dbus modules
from PyQt5.Qt import QDBusInterface
from PyQt5.Qt import QDBusReply
from checkbox_support.scripts.audio_settings import unlocalized_env


class PinPukTabDialog(QDialog):
    
    # member properties
    captionErr = "E' stato rilevato un errore"
    info = "Info"
    matchingError = "I %s immessi non corrispondono"
    lengthError = "Il %s immesso deve essere lungo almeno 5 caratteri"
    changeMsg = "Il %s è stato cambiato correttamente"
    unlockMsg = "Il %s è stato sbloccato correttamente"
    verifyMsg = "Il %s immesso è corretto"
    
    '''
    Tab dialog window for pin/puk managment features
    '''
    def __init__(self):
        '''
        Define the Tab dialog window
        '''
        super().__init__()
        
        # creating link to dbus
        # checking for deamon, smartcard and smartcard reader presence
        try:  
            self.dbusClient = DbusTokenManagerCallDaemon()
            self.dbusClient.getATR()
        except Exception as ex:
            msg,details = ex.args
            QMessageBox.warning(QMessageBox(), self.captionErr, details)
            self.destroy()
            return
        
        self.setLocale(QLocale(QLocale.Italian, QLocale.Italy))
        # define tab widget for tabs
        self.tabwidget = QTabWidget()
        self.tabList = []
        self.tabList.append(PinPukTab("c_pin"))
        self.tabList.append(PinPukTab("v_pin"))
        self.tabList.append(PinPukTab("u_pin"))
        self.tabList.append(PinPukTab("c_puk"))
        self.tabList.append(PinPukTab("v_puk"))
        self.tabwidget.addTab(self.tabList[0], "Cambia PIN")
        self.tabwidget.addTab(self.tabList[1], "Verifica PIN")
        self.tabwidget.addTab(self.tabList[2], "Sblocca PIN")
        self.tabwidget.addTab(self.tabList[3], "Cambia PUK")
        self.tabwidget.addTab(self.tabList[4], "Verifica PUK")
        
        # remaining attempts
        empyLine = QLabel("")
        self.remainingAttemptsLabel = QLabel()
        self.__getRemainingAttempts__()
        
        # creating buttonbox, cancel and ok button
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        cancel_btn = buttonbox.button(QDialogButtonBox.Cancel)
        ok_btn = buttonbox.button(QDialogButtonBox.Ok)
        buttonbox.setLayoutDirection(Qt.RightToLeft)
        buttonbox.setTabOrder(ok_btn , cancel_btn)
        ok_btn.clicked.connect(self.btnAction)
        cancel_btn.setText("Cancella")
        cancel_btn.clicked.connect(self.reject)
        
        # add buttonbox and tabwidget on mainLayout. Adding mainLayout on dialog window
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabwidget)
        mainLayout.addWidget(self.remainingAttemptsLabel)
        mainLayout.addWidget(empyLine)
        mainLayout.addWidget(buttonbox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle('Operazioni su Pin e Puk')
        self.setFixedHeight(300)
        self.setFixedWidth(550)
        self.exec_()
        
    def btnAction(self):
        """
            define an action to execute when you click "OK" button
        """
        # retrieving current tab to execute proper Token Manager operation.
        what = ["PIN", "PIN", "PIN", "PUK", "PUK"]
        currentIndex = self.tabwidget.currentIndex()         
        oldCode = self.tabList[currentIndex].oldTextLine.text()
        if currentIndex != 1 and currentIndex != 4:   
            newCode1 = self.tabList[currentIndex].newTextLine.text()
            newCode2 = self.tabList[currentIndex].newTextLine2.text()
        
            if newCode1 == newCode2 and PinPukTab.regExp.exactMatch(newCode1): 
                try:
                    if currentIndex == 0:
                        self.dbusClient.setPin(oldCode, newCode1)
                        QMessageBox.information(QMessageBox(), self.info, self.changeMsg % what[currentIndex])
                    elif currentIndex == 2:
                        self.dbusClient.unlockPKCS11Token(oldCode , newCode1)
                        QMessageBox.information(QMessageBox(), self.info, self.unlockMsg % what[currentIndex])
                    elif currentIndex == 3:
                        self.dbusClient.setPuk(oldCode, newCode1)
                        QMessageBox.information(QMessageBox(), self.info, self.changeMsg % what[currentIndex])
                    #if everything is ok dialog window is closed
                    self.reject()
                except Exception as ex:
                    msg,details = ex.args
                    QMessageBox.warning(QMessageBox(), self.captionErr, details)
            elif newCode1 == newCode2:
                QMessageBox.warning(QMessageBox(), self.captionErr, self.lengthError % what[currentIndex])
            elif PinPukTab.regExp.exactMatch(newCode1):
                QMessageBox.warning(QMessageBox(), self.captionErr, self.matchingError % what[currentIndex])
            else:
                QMessageBox.warning(
                                    QMessageBox(), 
                                    self.captionErr, 
                                    ((self.matchingError + "\n" + self.lengthError) % (what[currentIndex], what[currentIndex])))
        else:
            try:
                if currentIndex == 1:
                    self.dbusClient.verifyPin(oldCode)
                elif currentIndex == 4:
                    self.dbusClient.verifyPuk(oldCode)
                QMessageBox.information(QMessageBox(), self.info, self.verifyMsg % what[currentIndex])
                self.reject()
            except Exception as ex:
                    msg,details = ex.args
                    QMessageBox.warning(QMessageBox(), self.captionErr, details)
        
        # redefine remaining attemps if something is wrong
        self.__getRemainingAttempts__()
        self.repaint()
        
    #private procedures
    def __getRemainingAttempts__(self):
        try:
            pinAttempts = self.dbusClient.getPinRemainingAttempts()
        except Exception as ex:
            msg,details = ex.args
            pinAttempts = " - "
            QMessageBox.warning(QMessageBox(), self.captionErr, details)
        try:
            pukAttempts = self.dbusClient.getPukRemainingAttempts()
        except Exception as ex:
            msg,details = ex.args
            pukAttempts = " - "
            QMessageBox.warning(QMessageBox(), self.captionErr, details)
        self.remainingAttemptsLabel.setText(
                                            "Tentativi rimasti PIN: %s    Tentativi rimasti PUK: %s" % 
                                            (
                                             str(pinAttempts),
                                             str(pukAttempts)
                                            )
                                            )

class PinPukTab(QWidget):
    """
        Display a Widged for a pin/puk tab
    """
    
    # RegExp member property
    regExp = QRegExp("[0-9]{5,8}")
    
    def __init__(self, operation):
        super().__init__()
        
        if operation == "c_pin" or operation == "v_pin":
            oldStr = "PIN attuale"
            newStr = "Nuovo PIN"
            cNewStr = "Conferma nuovo PIN"
        elif operation == "c_puk" or operation == "v_puk":
            oldStr = "PUK attuale"
            newStr = "Nuovo PUK"
            cNewStr = "Conferma nuovo PUK"
        elif operation == "u_pin":
            oldStr = "PUK"
            newStr = "Nuovo PIN"
            cNewStr = "Conferma nuovo PIN"
        else:
            raise Exception("Errore generico", "Operazione non riconosciuta!")
        
        oldPinLabel = QLabel(oldStr)
        oldPinPukText = QLineEdit()
        oldPinPukText.setEchoMode(QLineEdit.Password)
        oldPinPukText.setFixedWidth(200)
        # oldPinPukText.setValidator(QRegExpValidator(QRegExp("[0-9]{5,8}")))
        self.oldTextLine = oldPinPukText
        
        if operation != "v_pin" and operation != "v_puk": 
            newPinLabel = QLabel(newStr)
            newPinPukText = QLineEdit()
            newPinPukText.setEchoMode(QLineEdit.Password)
            newPinPukText.setFixedWidth(200)
            newPinPukText.setValidator(QRegExpValidator(self.regExp))
            self.newTextLine = newPinPukText
            
            newPinLabel2 = QLabel(cNewStr)
            newPinPukText2 = QLineEdit()
            newPinPukText2.setEchoMode(QLineEdit.Password)
            newPinPukText2.setFixedWidth(200)
            newPinPukText2.setValidator(QRegExpValidator(self.regExp))
            # TODO check delle due pass
            self.newTextLine2 = newPinPukText2
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(oldPinLabel)
        mainLayout.addWidget(oldPinPukText)
        if operation != "v_pin" and operation != "v_puk": 
            mainLayout.addWidget(newPinLabel)
            mainLayout.addWidget(newPinPukText)
            mainLayout.addWidget(newPinLabel2)
            mainLayout.addWidget(newPinPukText2)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

class DbusTokenManagerCallDaemon(object):
    service = "it.libersoft.firmapiud.dbusinterface.TokenManagerInterface"
    path = "/it/libersoft/firmapiud/TokenManager"
    interface = "it.libersoft.firmapiud.dbusinterface.TokenManagerInterface"
    checkPinPuk = False

    def __init__(self):
        self.fpiudaemon = QDBusInterface(self.service, self.path, interface=self.interface,
                                    parent=None)
        self.fpiudaemon.setTimeout(120000)

    def login(self, pin):
        """
            Invoca il demone per loggarsi sul token crittografico
        """
        result = self.fpiudaemon.call("login", pin)
        return self.__replyVoidProcedure(result)
    
    def logout(self):
        """
            Invoca il demone per sloggarsi dal token crittografico
        """
        result = self.fpiudaemon.call("logout")
        return self.__replyVoidProcedure(result)
    
    def getATR(self):
        result = self.fpiudaemon.call("getATR")
        reply = QDBusReply(result)
        if result.type() == 3:
            raise Exception(reply.error().name(), reply.error().message())
        elif reply.isValid():
            return bytes(reply.value())
    
    def setPin(self, oldPin, newPin):
        return self.__setPinPukProcedure("setPin", oldPin, newPin)
            
    def setPuk(self, oldPuk, newPuk):
        return self.__setPinPukProcedure("setPuk", oldPuk, newPuk)

    def verifyPin(self, pin):
        return self.__verifyPinPuk("verifyPin", pin)
    
    def verifyPuk(self, puk):
        return self.__verifyPinPuk("verifyPuk", puk)
    
    def getPinRemainingAttempts(self):
        return self.__pinPukRemainingAttempts("getPinRemainingAttempts")
    
    def getPukRemainingAttempts(self):
        return self.__pinPukRemainingAttempts("getPukRemainingAttempts")
    
    def unlockPKCS11Token(self, puk, newPin):
        return self.__setPinPukProcedure("unlockPKCS11Token", puk, newPin)
    
    def __checkPin(self, pin):
        if self.checkPinPuk:
            length = len(pin)
            if not(pin.isnumeric() and length >= 5 and length <= 8):
                raise Exception(
                                "codice non valido!",
                                "Il pin/puk immesso deve contenere solo numeri ed essere compreso tra 5 e 8 caratteri")

    def __setPinPukProcedure(self, operation, oldPin, newPin):
        self.__checkPin(oldPin)
        self.__checkPin(newPin)
        result = self.fpiudaemon.call(operation, oldPin, newPin)
        return self.__replyVoidProcedure(result)
    
    def __verifyPinPuk(self, operation, pin):
        self.__checkPin(pin)
        result = self.fpiudaemon.call(operation, pin)
        return self.__replyResultProcedure(result)

    def __pinPukRemainingAttempts(self, operation):
        result = self.fpiudaemon.call(operation)
        return self.__replyResultProcedure(result)

    def __replyResultProcedure(self, result):
        reply = QDBusReply(result)
        if result.type() == 3:
            raise Exception(reply.error().name(), reply.error().message())
        elif reply.isValid():
            return reply.value()

    def __replyVoidProcedure(self, result):
        reply = QDBusReply(result)
        if result.type() == 3:
            raise Exception(reply.error().name(), reply.error().message())
        elif reply.isValid():
            pass
        else:
            raise Exception(
                            "risposta non valida",
                            "Il demone ha restituito una risposta non valida o che non riesco a capire")