#!/usr/bin/python3
# coding=utf-8

# Experimental test. this file has to be deleted when tests are over.

import sys
from PyQt5.Qt import QDialog
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

class PinPukTabDialog(QDialog):
    '''
    Tab dialog window for pin/puk managment features
    '''


    def __init__(self):
        '''
        Define the Tab dialog window
        '''
        super().__init__()
        self.setLocale(QLocale(QLocale.Italian,QLocale.Italy))
        #define tab widget for tabs
        tabwidget = QTabWidget()
        cPinTab = PinPukTab("c_pin")
        vPinTab = PinPukTab("v_pin")
        uPinTab = PinPukTab("u_pin")
        cPukTab = PinPukTab("c_puk")
        vPukTab = PinPukTab("v_puk")
        tabwidget.addTab(cPinTab,"Cambia PIN")
        tabwidget.addTab(vPinTab,"Verifica PIN")
        tabwidget.addTab(uPinTab,"Sblocca PIN")
        tabwidget.addTab(cPukTab,"Cambia PUK")
        tabwidget.addTab(vPukTab,"Verifica PUK")
        
        #remaining attempts
        empyLine = QLabel("")
        remainingAttemptsLabel = QLabel("Tentativi rimasti PIN: 3    Tentativi rimasti PUK: 10")
        
        #creating buttonbox, cancel and ok button
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        cancel_btn = buttonbox.button(QDialogButtonBox.Cancel)
        ok_btn= buttonbox.button(QDialogButtonBox.Ok)
        buttonbox.setLayoutDirection(Qt.RightToLeft)
        buttonbox.setTabOrder(ok_btn , cancel_btn)
        ok_btn.clicked.connect(ClasseScema)
        cancel_btn.setText("Cancella")
        cancel_btn.clicked.connect(self.reject)
        
        #add buttonbox and tabwidget on mainLayout. Adding mainLayout on dialog window
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabwidget)
        mainLayout.addWidget(remainingAttemptsLabel)
        mainLayout.addWidget(empyLine)
        mainLayout.addWidget(buttonbox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle('Operazioni su Pin e Puk')
        self.setFixedHeight(300)
        self.setFixedWidth(550)
        self.exec_()

class ClasseScema(QDialog):
    def __init__(self):
        print("Classe Scema eseguita")

class PinPukTab(QWidget):
    """
        Display a Widged for a pin/puk tab
    """
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
            raise Exception("Errore generico","Operazione non riconosciuta!")
        
        oldPinLabel = QLabel(oldStr)
        oldPinPukText =QLineEdit()
        oldPinPukText.setEchoMode(QLineEdit.Password)
        oldPinPukText.setFixedWidth(200)
        self.oldTextLine = oldPinPukText
        
        if operation != "v_pin" and operation != "v_puk": 
            newPinLabel = QLabel(newStr)
            newPinPukText =QLineEdit()
            newPinPukText.setEchoMode(QLineEdit.Password)
            newPinPukText.setFixedWidth(200)
            self.newTextLine = newPinPukText
            newPinPukText.setValidator(QRegExpValidator(QRegExp("[0-9]{5,8}")))
                       
            newPinLabel2 = QLabel(cNewStr)
            newPinPukText2 =QLineEdit()
            newPinPukText2.setEchoMode(QLineEdit.Password)
            newPinPukText2.setFixedWidth(200)
            #TODO check delle due pass
            #self.newTextLine = newPinPukText
        
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

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = PinPukTabDialog()
    app.show()
    #qt_app.exec()
    qt_app.deleteLater()