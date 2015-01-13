import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



class mainWindow(QWidget):
        
    def signfile(self):
        signDialog = QFileDialog
        signDialog.FileMode(1)
        listadeifile = signDialog.getOpenFileNames(caption="Scegli il file da firmare:")
        print (listadeifile[0])
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione sign 
        
        
    def versignfile(self):
        #listadeifile = QFileDialog.getOpenFileNames(caption="Scegli il file del quale verificare la firma:")
        #print (listadeifile[0])
        print('foofile')
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione verify     
        
    def signfolder(self):
        signFolderDialog = QFileDialog
        signFolderDialog.FileMode(2)
        #signFolderDialog.setOption(signFolderDialog.ShowDirsOnly, true)
        folder = signFolderDialog.getOpenFileNames(caption="Scegli la cartella da firmare:")
        for i in range(len(folder)):
            print(folder[0][i])
            #i++
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione sign 
        
        
    def versignfolder(self):
        #listadeifile = QFileDialog.getOpenFileNames(caption="Scegli il file del quale verificare la firma:")
        #print (listadeifile[0])
        print('fooverfold')
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione verify      
    
    
    
    
    
    
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)

        #Definisco la finestra
        self.setWindowTitle("Firmapiù")
 
        #Definisco la label per le azioni
        actionLabel = QLabel("Scegli l'azione da effettuare:")
        
        #Definisco il bottone Firma
        #TODO: Icona del bottone
        iconsignFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFile = QPushButton(QIcon(iconsignFile), 'F&irma')
        self.btnSignFile.sizeHint()
        self.btnSignFile.setToolTip("Firma il documento")        
        self.btnSignFile.clicked.connect(self.signfile)
        
        #Definisco il bottone FirmaCartella
        #TODO: Icona del bottone
        iconsignFolder = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFolder = QPushButton(QIcon(iconsignFolder), 'Firma &Cartella')
        self.btnSignFolder.sizeHint()
        self.btnSignFolder.setToolTip("Firma i file contenuti nella cartella")        
        self.btnSignFolder.clicked.connect(self.signfolder)
        
        #Definisco il bottone Verifica firma
        #TODO: Icona del bottone
        iconverFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnVerFile = QPushButton(QIcon(iconverFile), '&Verifica')
        self.btnVerFile.sizeHint()
        self.btnVerFile.setToolTip("Verifica la firma del documento")        
        self.btnVerFile.clicked.connect(self.versignfile)
        
        #Definisco il bottone Chiudi
        iconesc = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnEsc = QPushButton(QIcon(iconesc), '&Esci')
        self.btnEsc.sizeHint()
        self.btnEsc.setToolTip("Chiude l'applicazione")        
        self.btnEsc.clicked.connect(QCoreApplication.instance().quit)


        #Imposta il layout dei bottoni
        #fileChooserLayout = QHBoxLayout()
        #fileChooserLayout.addWidget(actionLabel)
        #fileChooserLayout.addWidget(self.btnFile)
        
        btnLayoutActions = QHBoxLayout()
        btnLayoutActions.addWidget(actionLabel)
        btnLayoutActions.addWidget(self.btnSignFile)
        btnLayoutActions.addWidget(self.btnVerFile)
        btnLayoutActions.addWidget(self.btnSignFolder)
        
        btnLayoutEsc = QHBoxLayout()
        btnLayoutEsc.addWidget(self.btnEsc)
        #Imposta il layout della finestra
        mainLayout = QGridLayout()
        #mainLayout.addLayout(fileChooserLayout, 0,0)
        mainLayout.addLayout(btnLayoutActions, 0,0)
        mainLayout.addLayout(btnLayoutEsc,1, 1)
        self.setLayout(mainLayout)
           
    
if __name__=='__main__':
    qt_app = QApplication(sys.argv)
    app=mainWindow()
    app.show()
    qt_app.exec()
    