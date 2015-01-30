#!/usr/bin/python3
import sys
import glob

from PyQt5.Qt import *


class DbusCallDaemon:
    fpiudaemon = QDBusInterface("it.libersoft.FirmapiuDInterface",
                                "/it/libersoft/FirmapiuD", interface = 'it.libersoft.FirmapiuDInterface',
                                parent = None)
    def test_connection(self):
        status = QDBusInterface("it.libersoft.FirmapiuDInterface",
                                "/it/libersoft/FirmapiuD", interface = 'org.freedesktop.DBus.Peer',
                                parent = None).call('Ping')
        if status.type() == 3:
            DialogFunctions.error_dialog('Errore', 'Il demone non è attivo,\nnon sarà possibile effettuare\nopearazioni'
                                                   ' che utilizzino la smartcard.')
        else:
            pass

    def sign(self, filepath, options):
        """

        :type options: dict
        """
        result = self.fpiudaemon.call('sign', filepath, options)
        reply = QDBusReply(result)
        if result.type() == 3:
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Operazione eseguita, controlla i log per'
                                                                   ' i dettagli')
            for i in range(len(filepath)):
                ActionFunctions.write_log(ActionFunctions, 'Ok! Il file è stato salvato come ' +
                                            reply.value()[filepath[i]])

    def verify(self, filepath):
        result = self.fpiudaemon.call('verify', filepath)
        reply = QDBusReply(result)
        if result.type() == 3:
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Operazione eseguita, controlla i log per'
                                                                   ' i dettagli')
            for i in range(len(filepath)):
                outstatus = reply.value()[filepath[i]]
                if outstatus.split(sep=':',maxsplit=1)[1]:
                    exit_text = 'Firma legalmente valida'
                else:
                    exit_text = outstatus.split(sep=':',maxsplit=1)[1]
                ActionFunctions.write_log(ActionFunctions, filepath[i] + ': ' + exit_text)


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
                DialogFunctions.error_dialog('PIN errato', 'Il PIN *deve* essere lungo '
                                             + str(pinlen) + ' caratteri')
                pin = DialogFunctions.pin_dialog(DialogFunctions())
                return pin
        else:
            DialogFunctions.error_dialog('Errore',
                                         'L\'azione non è stata completata a causa dell\'interruzione dell\'utente')

    def file_dialog(dialog_functions, action):
        filters = ''
        if action == 'sign':
            caption = 'Scegli il file da firmare:'
        elif action == 'verify':
            caption = 'Scegli il file da verificare:'
            filters = 'Signed Files(*.p7m *.p7s)'
        else:
            DialogFunctions.error_dialog('Errore', 'Azione sconosciuta')
            return False
        filelist = QFileDialog.getOpenFileNames(QFileDialog(), caption = caption, filter = filters)
        print(filelist)
        return filelist[0]

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
            DialogFunctions.error_dialog('Errore', 'Azione sconosciuta')
            return False
        folder = QFileDialog.getExistingDirectory(QFileDialog(), caption, filters)
        print(folder)
        return folder

    def error_dialog(caption, text):
        """

        :type caption: str
        :type text: str
        """
        QMessageBox.warning(QMessageBox(), caption, text)


class ActionFunctions(QWidget):
    #write_to_log = pyqtSignal(str)
    def sign_file(self, filelist=[]):
        options = {}
        if filelist == []:
            filelist = DialogFunctions.file_dialog(DialogFunctions(), 'sign')
        if filelist != []:
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.pin_dialog(DialogFunctions())
                if not (options['pin'] is None):
                    DbusCallDaemon('sign', filelist, options)
            else:
                DialogFunctions.error_dialog('Errore', 'Selezionare una cartella di destinazione '
                                                       'per il file firmato')


    def ver_sign_file(self, filelist=[]):
        if filelist == []:
            filelist = DialogFunctions.file_dialog(DialogFunctions(), 'verify')
        if filelist != []:
            for i in range(len(filelist)):
                DbusCallDaemon('verify', filelist, '')

    def sign_folder(self, folder=[]):
        options = {}
        if folder == []:
            folder = DialogFunctions.folder_dialog(DialogFunctions(), 'sign')
        files = glob.glob(folder + "/*.*")
        if (len(files) > 0):
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.pin_dialog
                DbusCallDaemon('sign', files, options)
        else:
            DialogFunctions.error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                                        " file oppure non è stata selezionata "
                                                        "nessuna cartella")

    def ver_sign_folder(self):
        folder = DialogFunctions.folder_dialog(DialogFunctions(), 'verify')
        files = glob.glob(folder + "/*.p7m*")
        files = files + glob.glob(folder + "/*.p7s*")
        if len(files) > 0:
            DbusCallDaemon('verify', files, '')
        else:
            DialogFunctions.error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                                        " file oppure non è stata selezionata nessuna"
                                                        " cartella")

    def write_log(self, text):
        #self.write_to_log.connect(MainWindow.log_area.append(text))
        #self.write_to_log.emit()
        MainWindow.log_area.append(text)


    def __init__(self, parent = None):
        super(ActionFunctions, self).__init__(parent)


class LabelDND(QLabel):
    def __init__(self,title, parent):
        super(LabelDND, self).__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
            e.accept()
        elif e.mimeData().hasFormat('application/pkcs7-mime'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        urls = (e.mimeData().urls())
        to_be_signed = []
        to_be_checked = []
        path = []
        for i in range(len(urls)):
            mime = QMimeType.name(QMimeDatabase().mimeTypeForFile(urls[i].toLocalFile()))
            if mime == 'application/pkcs7-mime':
                to_be_checked.append(urls[i].toLocalFile())
            elif mime == 'inode/directory':
                path.append(urls[i].toLocalFile())
            else:
                to_be_signed.append(urls[i].toLocalFile())
        print(to_be_checked)
        print(to_be_signed)
        print(path)
        if to_be_signed != []:
            ActionFunctions.sign_file(self,to_be_signed)
        if to_be_checked != []:
            ActionFunctions.ver_sign_file(self,to_be_checked)
        if path != []:
            ActionFunctions.sign_folder(self, path)


class MainWindow(QWidget):

    def uicreate(self):
        # super(MainWindow, self).__init__()
        windowicon = ""
        self.setWindowIcon(QIcon(windowicon))
        btnsize = QSize(125, 125)
        iconsize = QSize(50, 50)

        #Definisco la finestra
        self.setWindowTitle("FirmaPiù")
        self.setMaximumWidth(410)


        #Definisco la label per le azioni
        action_label = QLabel("Scegli l'azione da effettuare:")
        action_label.setAlignment(Qt.AlignHCenter)

        #Definisco il bottone Firma
        #TODO: Icona del bottone
        iconsign_file = ""
        MainWindow.btn_signFile = QPushButton(QIcon(iconsign_file), 'F&irma')
        MainWindow.btn_signFile.setFixedSize(btnsize)
        MainWindow.btn_signFile.setToolTip("Firma un documento")
        MainWindow.btn_signFile.clicked.connect(ActionFunctions.sign_file)


        #Definisco il bottone FirmaCartella
        #TODO: Icona del bottone
        iconsign_folder = ""
        MainWindow.btn_signFolder = QPushButton(QIcon(iconsign_folder), 'Firma &cartella')
        MainWindow.btn_signFolder.setFixedSize(btnsize)
        MainWindow.btn_signFolder.setToolTip("Firma tutti i documenti di una cartella")
        MainWindow.btn_signFolder.clicked.connect(ActionFunctions.sign_folder)

        #Definisco il bottone Verifica firma
        #TODO: Icona del bottone
        iconver_file = ""
        MainWindow.btn_verFile = QPushButton(QIcon(iconver_file), '&Verifica')
        MainWindow.btn_verFile.setFixedSize(btnsize)
        MainWindow.btn_verFile.setToolTip("Verfica la firma di un documento")
        MainWindow.btn_verFile.clicked.connect(ActionFunctions.ver_sign_file)

        #Definisco il bottone VerificafirmaCartella
        #TODO: Icona del bottone
        iconver_folder = ""
        MainWindow.btn_ver_folder = QPushButton(QIcon(iconver_folder), 'Verifica c&artella')
        MainWindow.btn_ver_folder.setFixedSize(btnsize)
        MainWindow.btn_ver_folder.setToolTip("Verifica la firma di tutti i documenti di una cartella")
        MainWindow.btn_ver_folder.clicked.connect(ActionFunctions.ver_sign_folder)

        #       Definisco il bottone Gestione PIN
        #TODO: Icona del bottone
        icon_manage_pin = ""
        MainWindow.btn_manage_pin = QPushButton(QIcon(icon_manage_pin), 'Gestisci\nil PIN')
        MainWindow.btn_manage_pin.setFixedSize(btnsize)
        MainWindow.btn_manage_pin.setToolTip("Permette di gestire il PIN (Cambio PIN/Sblocco PIN/Cambio PUK)")
        #TODO: Funzione che fa le cose

        #       Definisco il bottone Riconosci SmartCard
        #TODO: Icona del bottone
        icon_id_smartcard = ""
        MainWindow.btn_id_smartcard = QPushButton(QIcon(icon_id_smartcard), 'Riconoscimento\nSmartCard')
        MainWindow.btn_id_smartcard.setFixedSize(btnsize)
        MainWindow.btn_id_smartcard.setToolTip("Riconosimento del modello di SmartCard")
        #TODO: Funzione che fa le cose

        #Definisco il bottone Chiudi
        icon_esc = ""
        MainWindow.btn_esc = QPushButton('&Esci')
        MainWindow.btn_esc.setIcon(QIcon(icon_esc))
        MainWindow.btn_esc.setIconSize(iconsize)
        MainWindow.btn_esc.setFixedSize(btnsize)
        MainWindow.btn_esc.setToolTip("Chiude l'applicazione")
        MainWindow.btn_esc.clicked.connect(QCoreApplication.instance().quit)

        #Definisco la Drag and Drop area
        icon_dnd = ""
        MainWindow.btn_dnd = LabelDND('Droppa Qui', None)
        MainWindow.btn_dnd.setMinimumSize(300,150)





        #Definisco la log area

        MainWindow.log_area = QTextEdit()
        MainWindow.log_area.setReadOnly(True)
        MainWindow.log_area.setMinimumHeight(125)


        #       Definisco il layout generale

        label_layout = QHBoxLayout()
        label_layout.addWidget(action_label)

        btn_layout_1_row = QHBoxLayout()
        btn_layout_1_row.addWidget(MainWindow.btn_signFile)
        btn_layout_1_row.addWidget(MainWindow.btn_signFolder)
        btn_layout_1_row.addWidget(MainWindow.btn_verFile)

        btn_layout_2_row = QHBoxLayout()
        btn_layout_2_row.addWidget(MainWindow.btn_ver_folder)
        btn_layout_2_row.addWidget(MainWindow.btn_manage_pin)
        btn_layout_2_row.addWidget(MainWindow.btn_id_smartcard)

        btn_layout_3_row = QHBoxLayout()
        btn_layout_3_row.addWidget(MainWindow.btn_esc)
        btn_layout_3_row.addWidget(MainWindow.btn_esc)
        btn_layout_3_row.addWidget(MainWindow.btn_esc)

        log_area_layout = QHBoxLayout()
        log_area_layout.addWidget(MainWindow.log_area)

        btn_layout_dnd = QHBoxLayout()
        btn_layout_dnd.addWidget(MainWindow.btn_dnd)

        #Imposta il layout della finestra
        main_layout = QGridLayout()
        main_layout.addLayout(label_layout, 0, 0)
        main_layout.addLayout(btn_layout_1_row, 1, 0)
        main_layout.addLayout(btn_layout_2_row, 2, 0)
        main_layout.addLayout(btn_layout_3_row, 3, 0)
        main_layout.addLayout(btn_layout_dnd, 4, 0)
        main_layout.addLayout(log_area_layout, 5, 0)
        self.setLayout(main_layout)

    def __init__(self):
        super().__init__()
        self.uicreate()
        DbusCallDaemon.test_connection(self)



if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    app = MainWindow()
    app.show()
    qt_app.exec_()
    qt_app.deleteLater()