import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import glob

class mainWindow(QWidget):
        
    def signfile(self):
        signDialog = QFileDialog()
        filelist = signDialog.getOpenFileNames(caption="Scegli il file da firmare:")
        for i in range(len (filelist)-1):
                print(filelist[0][i])
        #TODO:Chiama il Java con rgomento listadeifile[0] e l'azione sign 
        
        
    def versignfile(self):
        verDialog = QFileDialog()
        filelist = verDialog.getOpenFileNames(caption="Scegli il file da verificare:",filter='Signed Files(*.p7m)')
        for i in range(len (filelist)-1):
                print(filelist[0][i])
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione verify     
        
    def signfolder(self):
        signFolderDialog = QFileDialog()
        folder = signFolderDialog.getExistingDirectory(self, 'Scegli la cartella da firmare:') #La caption non funziona
        files = glob.glob(folder+"/*.*")
        if len(files) > 0: 
            for i in range(len (files)):
                print(files[i])
        else:
            QMessageBox.warning(self, "No File","The selected folder doesn't contain any file or you didn't select any folder")
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione sign 
        
        
    def versignfolder(self):
        verFolderDialog = QFileDialog()
        folder = verFolderDialog.getExistingDirectory(self, 'Scegli la cartella da verificare:') #La caption non funziona
        files = glob.glob(folder+"/*.p7m*")
        if len(files) > 0: 
            for i in range(len (files)):
                print(files[i])
        else:
            QMessageBox.warning(self, "No File","The selected folder doesn't contain any valid file or you didn't select any folder")
        #TODO:Chiama il Java con argomento listadeifile[0] e l'azione verify      
    

    
    def __init__(self, parent=None):
        
        super(mainWindow, self).__init__(parent)
        windowicon = '/usr/share/icons/breeze/apps/scalable/klipper.svgz'
        self.setWindowIcon(QIcon(windowicon))
        size = QSize(200,200)
        
        #Definisco la finestra
        self.setWindowTitle("Firmapiù")
        #Definisco la label per le azioni
        actionLabel = QLabel("Scegli l'azione da effettuare:")
        actionLabel.setAlignment(Qt.AlignHCenter)
        
        #Definisco il bottone Firma
        #TODO: Icona del bottone
        iconsignFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFile = QPushButton(QIcon(iconsignFile), 'F&irma')
        self.btnSignFile.setMinimumSize(size)
        self.btnSignFile.setToolTip("Firma il documento")        
        self.btnSignFile.clicked.connect(self.signfile)
        
        #Definisco il bottone FirmaCartella
        #TODO: Icona del bottone
        iconsignFolder = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnSignFolder = QPushButton(QIcon(iconsignFolder), 'Firma &Cartella')
        self.btnSignFolder.setMinimumSize(size)   
        self.btnSignFolder.setToolTip("Firma i file contenuti nella cartella")        
        self.btnSignFolder.clicked.connect(self.signfolder)
        
        #Definisco il bottone Verifica firma
        #TODO: Icona del bottone
        iconverFile = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnVerFile = QPushButton(QIcon(iconverFile), '&Verifica')
        self.btnVerFile.setMinimumSize(size)
        self.btnVerFile.setToolTip("Verifica la firma del documento")        
        self.btnVerFile.clicked.connect(self.versignfile)
        
        #Definisco il bottone VerificafirmaCartella
        #TODO: Icona del bottone
        iconverFolder = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnVerFolder = QPushButton(QIcon(iconverFolder), 'Verifica c&artella')
        self.btnVerFolder.setMinimumSize(size)
        self.btnVerFolder.setToolTip("Verifica la firma dei documenti contenuti nella cartella")        
        self.btnVerFolder.clicked.connect(self.versignfolder)
        
        #Definisco il bottone Chiudi
        iconesc = "/usr/share/icons/breeze/actions/scalable/dialog-close.svgz"
        self.btnEsc = QPushButton(QIcon(iconesc), '&Esci')
        self.btnEsc.setMinimumSize(size)
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
        
        btnLayoutEsc = QHBoxLayout()
        btnLayoutEsc.addWidget(self.btnEsc)
        
        #Imposta il layout della finestra
        mainLayout = QGridLayout()
        mainLayout.addLayout(labelLayout,       0, 0)
        mainLayout.addLayout(btnLayoutSActions, 1, 0)
        mainLayout.addLayout(btnLayoutVActions, 2, 0)
        mainLayout.addLayout(btnLayoutEsc,      3, 0)
        self.setLayout(mainLayout)
           
    
if __name__=='__main__':
    qt_app = QApplication(sys.argv)
    app=mainWindow()
    app.show()
    qt_app.exec()
    
    