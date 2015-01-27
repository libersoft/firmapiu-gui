#!/usr/bin/python3
import sys
import glob

from PyQt5.Qt import *


class DbusCallDaemon:
    fpiudaemon = QDBusInterface("it.libersoft.FirmapiuDInterface",
                                "/it/libersoft/FirmapiuD", interface='it.libersoft.FirmapiuDInterface',
                                parent=None)

    def sign(self, filepath, options):
        """

        :type options: dict
        """
        result = self.fpiudaemon.call('sign', filepath, options)
        reply = QDBusReply(result)
        if result.type() == 3:
            error_dialog('Errore', result.errorMessage())
        else:
            for i in range(len(filepath)):
                DialogFunctions.info_dialog(DialogFunctions(), 'Info', reply.value()[filepath[i]])
                # mainWindow.write_log(None, reply.value()[filepath[i]])

    def verify(self, filepath):
        result = self.fpiudaemon.call('verify', filepath)
        reply = QDBusReply(result)
        if result.type() == 3:
            error_dialog('Errore', result.errorMessage())
        else:
            for i in range(len(filepath)):
                DialogFunctions.info_dialog(DialogFunctions(), 'Info', reply.value()[filepath[i]])

    def __init__(self, action, filepath, options):
        if action == 'sign':
            self.sign(filepath, options)
        elif action == 'verify':
            self.verify(filepath)
        else:
            print('Opzione non riconosciuta')


class DialogFunctions(QWidget):
    def info_dialog(self, caption, text):
        QMessageBox.information(QMessageBox(), caption, text)

    def pin_dialog(self):
        """

        :rtype : str
        """
        pinlen = 8
        pin = QInputDialog.getText(QInputDialog(), 'Inserisci il PIN', 'Inserisci il PIN della smartcard',
                                   QLineEdit.Password)
        if pin[1]:
            if len(pin[0]) == pinlen:
                return pin[0]
            else:
                error_dialog('PIN errato', 'Il PIN *deve* essere lungo '
                             + str(pinlen) + ' caratteri')
                pin = DialogFunctions.pin_dialog(DialogFunctions())
                return pin
        else:
            error_dialog('Errore', 'L\'azione non è stata completata a causa dell\'interruzione dell\'utente')

    def file_dialog(dialog_functions, action):
        filters = ''
        if action == 'sign':
            caption = 'Scegli il file da firmare:'
        elif action == 'verify':
            caption = 'Scegli il file da verificare:'
            filters = 'Signed Files(*.p7m *.p7s)'
        else:
            error_dialog('Errore', 'Azione sconosciuta')
            return False
        filelist = QFileDialog.getOpenFileNames(QFileDialog(), caption = caption, filter = filters)
        return filelist

    def folder_dialog(self, action):
        filters = ''
        if action == 'sign':
            caption = 'Scegli la cartella da firmare:'
        elif action == 'verify':
            caption = 'Scegli la cartella da verificare:'
            filters = 'Signed Files(*.p7m *.p7s)'
        elif action == 'outdir':
            caption = 'Scegli la cartella di destinazione'
        else:
            error_dialog('Errore', 'Azione sconosciuta')
            return False
        folder = QFileDialog.getExistingDirectory(QFileDialog(), caption, filters)
        return folder


def error_dialog(caption, text):
    """

    :type caption: str
    :type text: str
    """
    QMessageBox.warning(QMessageBox(), caption, text)


class ActionFunctions(QWidget):
    def signfile(self):
        options = {}
        filelist = DialogFunctions.file_dialog(DialogFunctions(), 'sign')
        if filelist[0] != []:
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.pin_dialog(DialogFunctions())
                if not (options['pin'] is None):
                    DbusCallDaemon('sign', filelist[0], options)
            else:
                error_dialog('Errore', 'Selezionare una cartella di destinazione '
                                       'per il file firmato')


    def versignfile(self):
        filelist = DialogFunctions.file_dialog(DialogFunctions(), 'verify')
        if filelist[0] != []:
            for i in range(len(filelist) - 1):
                DbusCallDaemon('verify', filelist[0], '')

    def signfolder(self):
        options = {}
        folder = DialogFunctions.folder_dialog(DialogFunctions(), 'sign')
        files = glob.glob(folder + "/*.*")
        if (len(files) > 0):
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.pin_dialog
                DbusCallDaemon('sign', files, options)
        else:
            error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                        " file oppure non è stata selezionata "
                                        "nessuna cartella")

    def versignfolder(self):
        folder = DialogFunctions.folder_dialog(DialogFunctions(), 'verify')
        files = glob.glob(folder + "/*.p7m*")
        files = files + glob.glob(folder + "/*.p7s*")
        if len(files) > 0:
            DbusCallDaemon('verify', files, '')
        else:
            error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                        " file oppure non è stata selezionata nessuna"
                                        " cartella")


# Stub of more detailed output
# for i in range(len(inpaths)):
# logArea.append('Il file '+inpaths[i] + 'è stato salvato come '+message[inpaths[i]]+'\n')


class MainWindow(QWidget):
    def write_log(self):
        self.log_area.append('test')

    def uicreate(self):
        #super(MainWindow, self).__init__()
        windowicon = ""
        self.setWindowIcon(QIcon(windowicon))
        btnsize = QSize(125, 125)
        iconsize = QSize(50, 50)

        #Definisco la finestra
        self.setWindowTitle("FirmaPiù")

        #Definisco la label per le azioni
        action_label = QLabel("Scegli l'azione da effettuare:")
        action_label.setAlignment(Qt.AlignHCenter)

        #Definisco il bottone Firma
        #TODO: Icona del bottone
        iconsign_file = ""
        self.btn_signFile = QPushButton(QIcon(iconsign_file), 'F&irma')
        self.btn_signFile.setFixedSize(btnsize)
        self.btn_signFile.setToolTip("Firma un documento")
        #self.btn_signFile.clicked.connect(ActionFunctions.signfile)
        self.btn_signFile.clicked.connect(MainWindow.write_log)
        #TODO Chiedi il PIN

        #Definisco il bottone FirmaCartella
        #TODO: Icona del bottone
        iconsign_folder = ""
        self.btn_signFolder = QPushButton(QIcon(iconsign_folder), 'Firma &cartella')
        self.btn_signFolder.setFixedSize(btnsize)
        self.btn_signFolder.setToolTip("Firma tutti i documenti di una cartella")
        self.btn_signFolder.clicked.connect(ActionFunctions.signfolder)

        #Definisco il bottone Verifica firma
        #TODO: Icona del bottone
        iconver_file = ""
        self.btn_verFile = QPushButton(QIcon(iconver_file), '&Verifica')
        self.btn_verFile.setFixedSize(btnsize)
        self.btn_verFile.setToolTip("Verfica la firma di un documento")
        self.btn_verFile.clicked.connect(ActionFunctions.versignfile)

        #Definisco il bottone VerificafirmaCartella
        #TODO: Icona del bottone
        iconver_folder = ""
        self.btn_ver_folder = QPushButton(QIcon(iconver_folder), 'Verifica c&artella')
        self.btn_ver_folder.setFixedSize(btnsize)
        self.btn_ver_folder.setToolTip("Verifica la firma di tutti i documenti di una cartella")
        self.btn_ver_folder.clicked.connect(ActionFunctions.versignfolder)

#       Definisco il bottone Gestione PIN
        #TODO: Icona del bottone
        icon_manage_pin = ""
        self.btn_manage_pin = QPushButton(QIcon(icon_manage_pin), 'Gestisci\nil PIN')
        self.btn_manage_pin.setFixedSize(btnsize)
        self.btn_manage_pin.setToolTip("Permette di gestire il PIN (Cambio PIN/Sblocco PIN/Cambio PUK)")
        #TODO: Funzione che fa le cose

#       Definisco il bottone Riconosci SmartCard
        #TODO: Icona del bottone
        icon_id_smartcard = ""
        self.btn_id_smartcard = QPushButton(QIcon(icon_id_smartcard), 'Riconoscimento\nSmartCard')
        self.btn_id_smartcard.setFixedSize(btnsize)
        self.btn_id_smartcard.setToolTip("Riconosimento del modello di SmartCard")
        #TODO: Funzione che fa le cose

        #Definisco il bottone Chiudi
        icon_esc = ""
        self.btn_esc = QPushButton('&Esci')
        self.btn_esc.setIcon(QIcon(icon_esc))
        self.btn_esc.setIconSize(iconsize)
        self.btn_esc.setFixedSize(btnsize)
        self.btn_esc.setToolTip("Chiude l'applicazione")
        self.btn_esc.clicked.connect(QCoreApplication.instance().quit)

        #Definisco la log area

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(125)
        self.log_area.append('Here the logs be will ')

        #Definisco il bottone Drag and Drop
        icon_dnd = ""
        self.btn_dnd = QTextEdit( )
        self.btn_dnd.append('Trascina qui per firmare o verificare')
        self.btn_dnd.setReadOnly(True)
        self.btn_dnd.setMinimumSize(300, 100)
        self.btn_dnd.setToolTip("Trascina qui per firmare o verificare")

        label_layout = QHBoxLayout()
        label_layout.addWidget(action_label)

        btn_layout_1_row = QHBoxLayout()
        btn_layout_1_row.addWidget(self.btn_signFile)
        btn_layout_1_row.addWidget(self.btn_signFolder)
        btn_layout_1_row.addWidget(self.btn_verFile)

        btn_layout_2_row = QHBoxLayout()
        btn_layout_2_row.addWidget(self.btn_ver_folder)
        btn_layout_2_row.addWidget(self.btn_manage_pin)
        btn_layout_2_row.addWidget(self.btn_id_smartcard)

        btn_layout_3_row = QHBoxLayout()
        btn_layout_3_row.addWidget(self.btn_esc)
        btn_layout_3_row.addWidget(self.btn_esc)
        btn_layout_3_row.addWidget(self.btn_esc)

        log_area_layout = QHBoxLayout()
        log_area_layout.addWidget(self.log_area)

        btn_layout_dnd = QHBoxLayout()
        btn_layout_dnd.addWidget(self.btn_dnd)

        #Imposta il layout della finestra
        main_layout = QGridLayout()
        main_layout.addLayout(label_layout,     0, 0)
        main_layout.addLayout(btn_layout_1_row, 1, 0)
        main_layout.addLayout(btn_layout_2_row, 2, 0)
        main_layout.addLayout(btn_layout_3_row, 3, 0)
        main_layout.addLayout(log_area_layout,  4, 0)
        main_layout.addLayout(btn_layout_dnd,   5, 0)
        self.setLayout(main_layout)

    def __init__(self):
        super().__init__()
        MainWindow.uicreate(self)


if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = MainWindow()
    app.show()
    qt_app.exec_()
    qt_app.deleteLater()
    sys.exit()