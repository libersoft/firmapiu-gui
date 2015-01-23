#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import glob
from PyQt5.QtDBus import *
from PyQt5.Qt import QDBusMessage


class dbus_call_daemon:
    fpiudaemon = QDBusInterface("it.libersoft.FirmapiuDInterface", 
                                "/it/libersoft/FirmapiuD", interface='it.libersoft.FirmapiuDInterface' ,
                                parent=None) 
    
    def sign(self, filepath, options ):
        result = self.fpiudaemon.call('sign',filepath,options)
        reply = QDBusReply(result)
        if result.type() == 3:
            dialog_functions.error_dialog(None, 'Errore', result.errorMessage())
        else:
            for i in range(len(filepath)):
                QMessageBox.information(None, 'Info', reply.value()[filepath[i]])   
            
    def verify(self, filepath):
        result = self.fpiudaemon.call('verify',filepath)
        reply = QDBusReply(result)
        if result.type() == 3:
            dialog_functions.error_dialog(None, 'Errore', result.errorMessage())
        else:
            for i in range(len(filepath)):
                QMessageBox.information(None, 'Info', reply.value()[filepath[i]])
                           
        
    def __init__(self, action, filepath, options):
        if action == 'sign':
            self.sign(filepath, options )
        elif action == 'verify':
            self.verify( filepath)
            
        else:
            print ('Opzione non riconosciuta')
  

class dialog_functions(QWidget):
    def error_dialog(self, caption, text):
        QMessageBox.warning(self, caption, text)
        
    def pin_dialog():
        pinlen = 8
        pin = QInputDialog.getText(None,"Inserisci il PIN", "Inserisci il PIN della smartcard", QLineEdit.Password)
        if pin[1]:
            if len(pin[0]) == pinlen:
                return pin[0]
            else:               
                dialog_functions.error_dialog(None,'PIN errato', 'Il PIN *deve* essere lungo '
                                               + str(pinlen) + ' caratteri')
                pin = dialog_functions.pin_dialog()
                return pin
        else:
            dialog_functions.error_dialog(None, 'Errore', "L'azione non è stata completata a causa dell'interruzione dell'utente")
    def file_dialog():
        pass
    
    def folder_dialog():
        pass
            

class action_functions(QWidget):
    def signfile(self):
        options = {}
        signDialog = QFileDialog()
        filelist = signDialog.getOpenFileNames(caption="Scegli il file da firmare:")
        if filelist[0] != []:
            options['outdir'] = QFileDialog.getExistingDirectory(None, 'Scegli la cartella dove salvare il file:') #La caption non funziona
            if options['outdir'] != '':
                options['pin'] = dialog_functions.pin_dialog()
                if not(options['pin'] == None):
                    dbus_call_daemon('sign', filelist[0],options)
            else:
                dialog_functions.error_dialog(None, 'Errore', 'Selezionare una cartella di destinazione per il file firmato')
                    
        
    def versignfile(self):
        verDialog = QFileDialog()
        filelist = verDialog.getOpenFileNames(caption="Scegli il file da verificare:",filter='Signed Files(*.p7m *.p7s)')
        if filelist[0] != []:
            for i in range(len (filelist)-1):
                dbus_call_daemon('verify',filelist[0],'')     
        
    def signfolder(self):
        options = {}
        signFolderDialog = QFileDialog()
        folder = signFolderDialog.getExistingDirectory(parent=None, caption='Scegli la cartella da firmare:') #La caption non funziona su KDE
        files = glob.glob(folder+"/*.*")
        if (len(files) > 0):
            options['outdir'] = QFileDialog.getExistingDirectory(None, 'Scegli la cartella dove salvare il file:')#La caption non funziona su KDE
            if options['outdir'] != '': 
                options['pin'] = dialog_functions.pin_dialog()
                dbus_call_daemon('sign', files, options)
        else:
            dialog_functions.error_dialog(None, "Nessun file", "La cartella selezionata non contiene nessun file oppure non è stata selezionata nessuna cartella")
        
    def versignfolder(self):
        verFolderDialog = QFileDialog()
        folder = verFolderDialog.getExistingDirectory(parent=None, caption='Scegli la cartella da verificare:') #La caption non funziona su KDE
        files = glob.glob(folder+"/*.p7m*")
        files = files + glob.glob(folder+"/*.p7s*")
        if len(files) > 0: 
            dbus_call_daemon('verify',files, '')
        else:
            dialog_functions.error_dialog(None, "Nessun file","La cartella selezionata non contiene nessun file oppure non è stata selezionata nessuna cartella")
            
#     Stub of more detailed output 
#         for i in range(len(inpaths)):
#             logArea.append('Il file '+inpaths[i] + 'è stato salvato come '+message[inpaths[i]]+'\n')
        
  
class mainWindow(QWidget):

    def uicreate(self):
        
        super(mainWindow, self).__init__()
        windowicon = '/usr/share/icons/breeze/apps/scalable/klipper.svgz'
        self.setWindowIcon(QIcon(windowicon))
        btnsize = QSize(150,150)
        iconsize = QSize(50,50)
        #Definisco la finestra
        self.setWindowTitle("Firmapiù")
        #Definisco la label per le azioni
        actionLabel = QLabel("Scegli l'azione da effettuare:")
        actionLabel.setAlignment(Qt.AlignHCenter)
        
        #Definisco il bottone Firma
        #TODO: Icona del bottone
        iconsignFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFile = QPushButton(QIcon(iconsignFile), 'F&irma')
        self.btnSignFile.setMinimumSize(btnsize)
        self.btnSignFile.setToolTip("Firma il documento")        
        self.btnSignFile.clicked.connect(action_functions.signfile)
        #TODO Chiedi il PIN
        
        #Definisco il bottone FirmaCartella
        #TODO: Icona del bottone
        iconsignFolder = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFolder = QPushButton(QIcon(iconsignFolder), 'Firma &Cartella')
        self.btnSignFolder.setMinimumSize(btnsize)   
        self.btnSignFolder.setToolTip("Firma i file contenuti nella cartella")        
        self.btnSignFolder.clicked.connect(action_functions.signfolder)
        
        #Definisco il bottone Verifica firma
        #TODO: Icona del bottone
        iconverFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnVerFile = QPushButton(QIcon(iconverFile), '&Verifica')
        self.btnVerFile.setMinimumSize(btnsize)
        self.btnVerFile.setToolTip("Verifica la firma del documento")        
        self.btnVerFile.clicked.connect(action_functions.versignfile)
        
        #Definisco il bottone VerificafirmaCartella
        #TODO: Icona del bottone
        iconverFolder = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnVerFolder = QPushButton(QIcon(iconverFolder), 'Verifica c&artella')
        self.btnVerFolder.setMinimumSize(btnsize)
        self.btnVerFolder.setToolTip("Verifica la firma dei documenti contenuti nella cartella")        
        self.btnVerFolder.clicked.connect(action_functions.versignfolder)
        
        #Definisco la log area
        
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)
        self.logArea.setMaximumHeight(300)
        self.logArea.append('Here the logs be will ') 
                            
        #Definisco il bottone Chiudi
        iconesc = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        #self.btnEsc = QPushButton(QIcon(iconesc), '&Esci')
        self.btnEsc = QPushButton()
        self.btnEsc.setIcon(QIcon(iconesc))
        self.btnEsc.setIconSize(iconsize)
        self.btnEsc.setMinimumSize(150,100)
        self.btnEsc.setToolTip("Chiude l'applicazione")        
        self.btnEsc.clicked.connect(QCoreApplication.instance().quit)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(actionLabel)
        
        btnLayoutSActions = QHBoxLayout()
        btnLayoutSActions.addWidget(self.btnSignFile)
        btnLayoutSActions.addWidget(self.btnSignFolder)
        
        btnLayoutVActions = QHBoxLayout()
        btnLayoutVActions.addWidget(self.btnVerFile)
        btnLayoutVActions.addWidget(self.btnVerFolder)
        
        logAreaLayout = QHBoxLayout()
        logAreaLayout.addWidget(self.logArea)
        
        btnLayoutEsc = QHBoxLayout()
        btnLayoutEsc.addWidget(self.btnEsc)
        
        #Imposta il layout della finestra
        mainLayout = QGridLayout()
        mainLayout.addLayout(labelLayout,       0, 0)
        mainLayout.addLayout(btnLayoutSActions, 1, 0)
        mainLayout.addLayout(btnLayoutVActions, 2, 0)
        mainLayout.addLayout(logAreaLayout,     3,  0)
        mainLayout.addLayout(btnLayoutEsc,      4, 0)
        self.setLayout(mainLayout)
    def __init__(self):
        mainWindow.uicreate(self)
           
if __name__=='__main__':
    qt_app = QApplication(sys.argv)
    app=mainWindow()
    app.show()
    qt_app.exec()
    
    