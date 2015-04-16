#!/usr/bin/python3
# coding=utf-8
# Copyright (C) 2015 Valerio Baldisserotto <svalo[at]libersoft[dot]it”

#This file is part of firmapiu-gui.
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
import glob

from PyQt5.Qt import *


class DbusCallDaemon:
    fpiudaemon = QDBusInterface("it.libersoft.firmapiud.dbusinterface.FirmapiuDInterface",
                                "/it/libersoft/firmapiud/FirmapiuD",
                                interface = 'it.libersoft.firmapiud.dbusinterface.FirmapiuDInterface',
                                parent = None)
    def test_connection(self):
        status = QDBusInterface("it.libersoft.firmapiud.dbusinterface.FirmapiuDInterface",
                                "/it/libersoft/firmapiud/FirmapiuD",
                                interface = 'org.freedesktop.DBus.Peer',
                                parent = None).call('Ping')
        if status.type() == 3:
            DialogFunctions.error_dialog('Errore', 'Il demone non è attivo,\nnon sarà possibile effettuare\nopearazioni'
                                                   ' che utilizzino la smartcard.')
            MainWindow.btn_signFile.setDisabled(True)
            MainWindow.btn_signFolder.setDisabled(True)
            MainWindow.btn_verFile.setDisabled(True)
            MainWindow.btn_ver_folder.setDisabled(True)
            MainWindow.btn_dnd.setAcceptDrops(False)
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
                if outstatus.split(sep=':', maxsplit=1)[1] == ' true':
                    exit_text = 'Firma legalmente valida'
                else:
                    exit_text = outstatus.split(sep=':', maxsplit=1)[1]
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

    def file_dialog(self, action):
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
        return filelist[0]

    def folder_dialog(self, action, default_path=''):
        filters = ''
        if action == 'sign':
            caption = 'Scegli la cartella da firmare:'
        elif action == 'verify':
            caption = 'Scegli la cartella da verificare:'
            filters = 'Signed Files(*.p7m *.p7s)'
        elif action == 'outdir':
            caption = 'Scegli la cartella di destinazione'
            folder = QFileDialog.getExistingDirectory(QFileDialog(), caption=caption, directory=default_path)
            return folder
        else:
            DialogFunctions.error_dialog('Errore', 'Azione sconosciuta')
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
    def sign_file(self, filelist=[], outdir=''):
        options = {}
        options['outdir'] = outdir
        if not filelist:
            filelist = DialogFunctions.file_dialog(DialogFunctions(), 'sign')
        if filelist:
            filepath = QFileInfo(filelist[0]).canonicalPath()
            if options['outdir'] == '':
                options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir', filepath)
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
        DbusCallDaemon('verify', filelist, '')

    def sign_folder(self, folder=[]):
        options = {}
        if folder == []:
            folder = DialogFunctions.folder_dialog(DialogFunctions(), 'sign')
        files = glob.glob(folder + "/*.*")
        if (len(files) > 0):
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.pin_dialog(DialogFunctions())
                DbusCallDaemon('sign', files, options)
        else:
            DialogFunctions.error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                                        " file oppure non è stata selezionata "
                                                        "nessuna cartella")

    def ver_sign_folder(self):
        folder = DialogFunctions.folder_dialog(DialogFunctions(), 'verify')
        files = glob.glob(folder + "/*.p7m*")
        files = files + glob.glob(folder + "/*.p7s*")
        if files:
            DbusCallDaemon('verify', files, '')
        else:
            DialogFunctions.error_dialog("Nessun file", "La cartella selezionata non contiene nessun"
                                                        " file oppure non è stata selezionata nessuna"
                                                        " cartella")

    def write_log(self, text):
        MainWindow.log_area.append(text)

    def change_code(self, what, oldcode, newcode):

    def verify_code(self, what, code):

    def get_remainging_attempts(self, what):

    def get_ATR(self, id):

    def unlock_PKCS11_token(self, id):

    def __init__(self, parent = None):
        super(ActionFunctions, self).__init__(parent)


class LabelDND(QLabel):
    def __init__(self, title, parent):
        super(LabelDND, self).__init__(title, parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setAlignment(Qt.AlignCenter)
        self.setToolTip('Trascina qua sopra i documenti che vuoi firmare.\n'
                        'Se trascini una cartella, saranno firmati ciascuno dei file contenuti.\n'
                        'Se trascini un file firmato, sarà verificato.')

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
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
            if (mime == 'application/pkcs7-mime') or (mime == 'application/pkcs7-signature'):
                to_be_checked.append(urls[i].toLocalFile())
            elif mime == 'inode/directory':
                path.append(urls[i].toLocalFile())
            else:
                to_be_signed.append(urls[i].toLocalFile())

        if len(to_be_checked) == 1:
            ActionFunctions.ver_sign_file(ActionFunctions(), to_be_checked)
        elif len(to_be_checked) > 1:
            to_be_signed.append(to_be_checked)
            DialogFunctions.info_dialog(DialogFunctions(), 'Attenzione', 'Stai per firmare un documento già firmato')
        else:
            pass
        if len(to_be_signed) > 0:
            outdir = QFileInfo(urls[0].path()).canonicalPath()
            ActionFunctions.sign_file(ActionFunctions(), to_be_signed, outdir)
        if len(path) > 0:
            ActionFunctions.sign_folder(ActionFunctions(), path[0])

class MainWindow(QWidget):

    def uicreate(self):
        iconpath = sys.exec_prefix+ "/share/firmapiu-gui/data/icons/tango-like/"
        windowicon = iconpath+"fpiu.svg"
        self.setWindowIcon(QIcon(windowicon))
        #btnsize = QSize(125, 125)
        btnsize = iconsize = QSize(96, 96)

#       Definisco la finestra
        self.setWindowTitle("FirmaPiù")
        self.setMaximumWidth(410)


#       Definisco la label per le azioni
        action_label = QLabel("Scegli l'azione da effettuare:")
        action_label.setAlignment(Qt.AlignHCenter)

#       Definisco il bottone Firma
#TODO: Icona del bottone
        iconsign_file = iconpath+"firma96x96.png"
        MainWindow.btn_signFile = QPushButton(QIcon(iconsign_file), '')
        MainWindow.btn_signFile.setIconSize(iconsize)
        MainWindow.btn_signFile.setFixedSize(btnsize)
        MainWindow.btn_signFile.setToolTip("Firma un documento")
        MainWindow.btn_signFile.clicked.connect(ActionFunctions.sign_file)

#       Definisco il bottone FirmaCartella
#TODO: Icona del bottone
        iconsign_folder = iconpath+"96px-Document-open.svg.png"
        MainWindow.btn_signFolder = QPushButton(QIcon(iconsign_folder), '')
        MainWindow.btn_signFolder.setFixedSize(btnsize)
        MainWindow.btn_signFolder.setIconSize(iconsize)
        MainWindow.btn_signFolder.setToolTip("Firma tutti i documenti di una cartella")
        MainWindow.btn_signFolder.clicked.connect(ActionFunctions.sign_folder)

#       Definisco il bottone Verifica firma
#TODO: Icona del bottone
        iconver_file = iconpath+"verifica96x96.png"
        MainWindow.btn_verFile = QPushButton(QIcon(iconver_file), '')
        MainWindow.btn_verFile.setIconSize(iconsize)
        MainWindow.btn_verFile.setFixedSize(btnsize)
        MainWindow.btn_verFile.setToolTip("Verfica la firma di un documento")
        MainWindow.btn_verFile.clicked.connect(ActionFunctions.ver_sign_file)

#       Definisco il bottone VerificafirmaCartella
#TODO: Icona del bottone
        iconver_folder = ""
        MainWindow.btn_ver_folder = QPushButton(QIcon(iconver_folder), 'Verifica c&artella')
        MainWindow.btn_ver_folder.setFixedSize(btnsize)
        MainWindow.btn_ver_folder.setToolTip("Verifica la firma di tutti i documenti di una cartella")
        MainWindow.btn_ver_folder.clicked.connect(ActionFunctions.ver_sign_folder)

#       Definisco il bottone Gestione PIN
#TODO: Icona del bottone
        icon_manage_pin = iconpath+"impostazioni96x96.png"
        MainWindow.btn_manage_pin = QPushButton(QIcon(icon_manage_pin), '')
        MainWindow.btn_manage_pin.setFixedSize(btnsize)
        MainWindow.btn_manage_pin.setIconSize(iconsize)
        MainWindow.btn_manage_pin.setToolTip("Permette di gestire il PIN (Cambio PIN/Sblocco PIN/Cambio PUK)")
        MainWindow.btn_manage_pin.clicked.connect(ActionFunctions.change_code)
#TODO: Funzione che fa le cose

#       Definisco il bottone Riconosci SmartCard
#TODO: Icona del bottone
        icon_id_smartcard = iconpath+"smartcardsets96x96.png"
        MainWindow.btn_id_smartcard = QPushButton(QIcon(icon_id_smartcard), '')
        MainWindow.btn_id_smartcard.setFixedSize(btnsize)
        MainWindow.btn_id_smartcard.setIconSize(iconsize)
        MainWindow.btn_id_smartcard.setToolTip("Riconosimento del modello di SmartCard")
        MainWindow.btn_id_smartcard.clicked.connect(ActionFunctions.get_ATR)
#TODO: Funzione che fa le cose

#       Definisco il bottone Chiudi
        icon_esc = iconpath+"window-close-symbolic.png"
        MainWindow.btn_esc = QPushButton('')
        MainWindow.btn_esc.setIcon(QIcon(icon_esc))
        MainWindow.btn_esc.setIconSize(iconsize)
        MainWindow.btn_esc.setFixedSize(btnsize)
        MainWindow.btn_esc.setToolTip("Chiude l'applicazione")
        MainWindow.btn_esc.clicked.connect(QCoreApplication.instance().quit)

#       Definisco la Drag and Drop area
        MainWindow.btn_dnd = LabelDND('Trascina qui per firmare\n(anche cartelle intere)', None)
        MainWindow.btn_dnd.setMinimumSize(300, 100)


#       Definisco la label per il log
        log_label = QLabel("Area di log:")
        log_label.setAlignment(Qt.AlignHCenter)

#       Definisco la log area
        MainWindow.log_area = QTextEdit()
        MainWindow.log_area.setReadOnly(True)
        MainWindow.log_area.setMinimumHeight(100)


#       Definisco il layout generale

        label_layout = QHBoxLayout()
        label_layout.addWidget(action_label)

        btn_layout_1_row = QHBoxLayout()
        btn_layout_1_row.addWidget(MainWindow.btn_signFile)
        btn_layout_1_row.addWidget(MainWindow.btn_signFolder)
        btn_layout_1_row.addWidget(MainWindow.btn_verFile)

        btn_layout_2_row = QHBoxLayout()
#        btn_layout_2_row.addWidget(MainWindow.btn_ver_folder)
        btn_layout_2_row.addWidget(MainWindow.btn_manage_pin)
        btn_layout_2_row.addWidget(MainWindow.btn_id_smartcard)
        btn_layout_2_row.addWidget(MainWindow.btn_esc)

#        btn_layout_3_row = QHBoxLayout()
#        btn_layout_3_row.addWidget(MainWindow.btn_esc)
#        btn_layout_3_row.addWidget(MainWindow.btn_esc)
#        btn_layout_3_row.addWidget(MainWindow.btn_esc)

        log_area_layout = QVBoxLayout()
        log_area_layout.addWidget(log_label)
        log_area_layout.addWidget(MainWindow.log_area)

        btn_layout_dnd = QHBoxLayout()
        btn_layout_dnd.addWidget(MainWindow.btn_dnd)

#       Imposta il layout della finestra
        main_layout = QGridLayout()
        main_layout.addLayout(label_layout, 0, 0)
        main_layout.addLayout(btn_layout_1_row, 1, 0)
        main_layout.addLayout(btn_layout_2_row, 2, 0)
        #main_layout.addLayout(btn_layout_3_row, 3, 0)
        main_layout.addLayout(btn_layout_dnd, 4, 0)
        main_layout.addLayout(log_area_layout, 5, 0)
        self.setLayout(main_layout)

    def __init__(self):
        super().__init__()
        self.uicreate()
        DbusCallDaemon.test_connection(self)
