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
    service = "it.libersoft.firmapiud.dbusinterface.FirmapiuDInterface"
    path = "/it/libersoft/firmapiud/FirmapiuD"
    interface = 'it.libersoft.firmapiud.dbusinterface.FirmapiuDInterface'

    def test_connection(self):
        interface = 'org.freedesktop.DBus.Peer'
        status = QDBusInterface(DbusCallDaemon.interface , DbusCallDaemon.path , interface = interface,
                                parent = None).call('Ping')
        if status.type() == 3:
            DialogFunctions.error_dialog('Errore', 'Il demone non è attivo,\nnon sarà possibile effettuare\nopearazioni'
                                                   ' che utilizzino la smartcard.')

            self.btn_signFile.setDisabled(True)
            self.btn_signFolder.setDisabled(True)
            self.btn_verFile.setDisabled(True)
            self.btn_ver_folder.setDisabled(True)
            self.btn_manage_pin.setDisabled(True)
            self.btn_dnd.setAcceptDrops(False)
        else:
            pass

    def sign(self, filepath, options):
        """

        :type options: dict
        """
        fpiudaemon = QDBusInterface(self.service, self.path, interface = self.interface,
                                    parent = None)
        fpiudaemon.setTimeout(120000)
        result = fpiudaemon.call('sign', filepath, options)
        reply = QDBusReply(result)
        if result.type() == 3:
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            #TODO lo vogliamo sto messaggio?
            #DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Operazione conclusa, controlla i log per'
            #                                                       ' i dettagli')
            for i in range(len(filepath)):
                if (type (reply.value()[filepath[i]]) is str):
                    #todo dai il nome del file sorgente
                    MainWindow.log_area.append('<p backgroud-color:"red"><big>Ok!</big> Il file è stato salvato come ' +'<big>' +
                                                reply.value()[filepath[i]] + '</big></p>')
                else:
                    MainWindow.log_area.append('<p backgroud-color:"#ff00cc"><big>Errore</big>, il documento ' +  filepath[i] +
                                               ' non è stato firmato</p>')
                    DialogFunctions.error_dialog('Errore', 'Errore ' + str(reply.value()[filepath[i]][0]) + ':\n'
                                                 + reply.value()[filepath[i]][1] + '\n\n')

    def verify(self, filepath):
        fpiudaemon = QDBusInterface(self.service, self.path, interface = self.interface,
                                    parent = None)
        fpiudaemon.setTimeout(120000)
        result = fpiudaemon.call('verify', filepath)
        reply = QDBusReply(result)
        if result.type() == 3:
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Firma valida\ncontrolla il log per'
                                                                   ' i dettagli')
            for i in range(len(filepath)):
                outstatus = reply.value()[filepath[i]]
                if outstatus.split(sep=':', maxsplit=1)[1] == ' true':
                    exit_text = 'Firma legalmente valida'
                else:
                    exit_text = outstatus.split(sep=':', maxsplit=1)[1]
                text = '<p><font color="red">' + filepath[i] + ': <big>' + exit_text + '</big></font></p>'
                ActionFunctions.write_log(ActionFunctions, text)

    def verifySingle(self, filepath, options={}):
        fpiudaemon = QDBusInterface(self.service, self.path, interface = self.interface,
                                    parent = None)
        fpiudaemon.setTimeout(120000)
        result = fpiudaemon.call('verifySingle', QDBusVariant(filepath), options )
        reply = QDBusReply(result)
        if result.type() == 3:
            text = '<p>Il file <big>' + filepath + ' NON </big> è un file p7m valido </p>'
            ActionFunctions.write_log(ActionFunctions, text)
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            legal = reply.value()[0]['legallysigned']
            tech = reply.value()[0]['oksigned']
            if legal and tech:
                text = '<p>Il file <big>' + filepath + '</big> risulta legalmente e tecnicamente valido</p>'
                ActionFunctions.write_log(ActionFunctions, text)
                DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Firma legalmente e tecnicamente valida,'
                                                                       '\ncontrolla il log per i dettagli')
            else :
                text = '<p>Il file <big>' + filepath + ' NON </big> è un file p7m valido </p>'
                ActionFunctions.write_log(ActionFunctions, text)
                DialogFunctions.error_dialog('Errore', 'Il file <big>non</big> è legalmente e tecnicamente valido')

    def pin_puk_ops(self, what, code, newcode=None):
        '''
        pin_puk_ops must be called with Pin or Puk case sensitive
        '''
        interface = "it.libersoft.firmapiud.dbusinterface.TokenManagerInterface"
        path = "/it/libersoft/firmapiud/TokenManager"

        fpiudaemon = QDBusInterface(self.service, path, interface = interface, parent = None)

        if newcode:
            result = fpiudaemon.call('set'+what, code, newcode)
        else:
            result = fpiudaemon.call('verify'+what, code)
        if result.type() == 3:
            DialogFunctions.error_dialog('Errore', result.errorMessage())
        else:
            if newcode:
                DialogFunctions.info_dialog(DialogFunctions(), 'Info', what + 'cambiato con successo')
            else:
                DialogFunctions.info_dialog(DialogFunctions(), 'Info', 'Il '+what+' è corretto')


    def __init__(self, action, filepath, options):
        if action == 'sign':
            self.sign(filepath, options)
        elif action == 'verify':
            self.verify(filepath)
        elif action == 'verifySingle':
            self.verifySingle(filepath, options)
        else:
            print('Opzione non riconosciuta')


class DialogFunctions(QWidget):
    def info_dialog(self, caption, text):
        QMessageBox.information(QMessageBox(), caption, text)

    def code_dialog(what):
        """


        :param what:
        :rtype : str
        """
        code_min_len = 5
        code_max_len = 8
        code = QInputDialog.getText(QInputDialog(), 'Inserisci il '+what, 'Inserisci il '+what+' della smartcard',
                                   QLineEdit.Password)
        if code[1]:
            if code_min_len <= len(code[0]) <= code_max_len:
                return code[0]
            else:
                DialogFunctions.error_dialog(what+' errato', 'Il '+what+ ' <b>deve</b> essere compreso fra '
                                             + str(code_min_len) + ' e '  + str(code_max_len) + ' caratteri')
                code = DialogFunctions.code_dialog(what)
                return code
        else:
            DialogFunctions.error_dialog('Errore',
                                         'L\'azione non è stata completata a causa dell\'interruzione dell\'utente')

    def file_dialog(self, action):
        filters = ''
        if action == 'sign':
            caption = 'Scegli il file da firmare:'
            filelist = QFileDialog.getOpenFileNames(QFileDialog(), caption = caption, filter = filters)
            return filelist[0]
        elif action == 'verify':
            caption = 'Scegli il file da verificare:'
            filters = 'Signed Files(*.p7m *.p7s)'
            file = QFileDialog.getOpenFileName(QFileDialog(), caption = caption, filter = filters)
            return file[0]
        else:
            DialogFunctions.error_dialog('Errore', 'Azione sconosciuta')
            return False


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
                options['pin'] = DialogFunctions.code_dialog('Pin')
                if (options['pin']):
                    DbusCallDaemon('sign', filelist, options)
            else:
                DialogFunctions.error_dialog('Errore', 'Selezionare una cartella di destinazione '
                                                       'per il file firmato')


    def ver_sign_file(self, file=''):
        options = {}
        if file == '':
            file = DialogFunctions.file_dialog(DialogFunctions(), 'verify')
        if file != '':
            DbusCallDaemon('verifySingle', file, options)

    def sign_folder(self, folder=[]):
        options = {}
        if folder == []:
            folder = DialogFunctions.folder_dialog(DialogFunctions(), 'sign')
        files = glob.glob(folder + "/*.*")
        if (len(files) > 0):
            options['outdir'] = DialogFunctions.folder_dialog(DialogFunctions(), 'outdir')
            if options['outdir'] != '':
                options['pin'] = DialogFunctions.code_dialog('Pin')
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
        pass

    def verify_code(self, what, code):
        pass

    def get_remainging_attempts(self, what):
        pass

    def get_ATR(self, id):
        pass

    def unlock_PKCS11_token(self, id):
        pass

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
            ActionFunctions.ver_sign_file(ActionFunctions(), to_be_checked[0])
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

class ChangeCodes(QDialog):
    def PinWindow(self):
        QDialog.__init__(self)
        
        height=40
        width = 100
        verify_width = 130
        
        self.setWindowTitle('Operazioni su Pin e Puk')
        
        self.pintext = QTextEdit(self)
        self.pintext.setPlaceholderText('Pin')
        self.pintext.setToolTip('Inserisci il Pin\nper cambiarlo o verificarlo')
        self.pintext.setMaximumHeight(height)
        self.pintext.setFixedWidth(width)

        self.btn_change_pin = QPushButton('Cambia Pin')
        self.btn_change_pin.setToolTip('Cambia il Pin della smartcard')
        self.btn_change_pin.setMaximumHeight(height)
        self.btn_change_pin.setFixedWidth(width)
        
        self.btn_verify_pin = QPushButton('Verifica il Pin')
        self.btn_verify_pin.setToolTip('Verifica la correttezza del Pin')
        self.btn_verify_pin.setMaximumHeight(height)
        self.btn_verify_pin.setFixedWidth(verify_width)

        self.puktext = (QTextEdit(self))
        self.puktext.setPlaceholderText('Puk')
        self.puktext.setToolTip('Inserischi il Puk\nper cambiarlo o verificarlo')
        self.puktext.setMaximumHeight(height)
        self.puktext.setFixedWidth(width)

        self.btn_change_puk = QPushButton('Cambia Puk')
        self.btn_change_puk.setToolTip('Cambia il Puk della smartcard')
        self.btn_change_puk.setMaximumHeight(height)
        self.btn_change_puk.setFixedWidth(width)

        self.btn_verify_puk = QPushButton('Verifica il Puk')
        self.btn_verify_puk.setToolTip('Verifica la correttezza del Puk')
        self.btn_verify_puk.setMaximumHeight(height)
        self.btn_verify_puk.setFixedWidth(verify_width)

        self.btn_esc = QPushButton('Esci')
        self.btn_esc.setMaximumHeight(height)
        self.btn_esc.clicked.connect(self.reject)

        self.pin_layout = QHBoxLayout()
        self.pin_layout.addWidget(self.pintext)
        self.pin_layout.addWidget(self.btn_change_pin)
        self.pin_layout.addWidget(self.btn_verify_pin)

        self.puk_layout = QHBoxLayout()
        self.puk_layout.addWidget(self.puktext)
        self.puk_layout.addWidget(self.btn_change_puk)
        self.puk_layout.addWidget(self.btn_verify_puk)

        self.esc_layout = QHBoxLayout()
        self.esc_layout.addWidget(self.btn_esc)

        self.layout = QGridLayout()
        self.layout.addLayout(self.pin_layout, 1, 0)
        self.layout.addLayout(self.puk_layout, 2, 0)
        self.layout.addLayout(self.esc_layout, 3, 0)
        self.setLayout(self.layout)


        #self.pintext.testo_cambiato.connect(self.testsignal)
        #self.pintext.textChanged.connect(self.pintext.testo_cambiato.emit)


        self.exec_()


    def __init__(self):
        super().__init__()
        self.pinWindow()


class MainWindow(QWidget):

    def uicreate(self):
        QWidget.__init__(self)

        iconpath = sys.exec_prefix+ "/share/firmapiu-gui/data/icons/tango-like/"
        windowicon = iconpath+"fpiu.svg"
        self.setWindowIcon(QIcon(windowicon))
        #btnsize = QSize(125, 125)
        btnsize = iconsize = QSize(96, 96)

#       Definisco la finestra
        self.setWindowTitle("FirmaPiù")
        self.setMaximumWidth(410)


#       Definisco la label per le azioni
        self.action_label = QLabel("Scegli l'azione da effettuare:")
        self.action_label.setAlignment(Qt.AlignHCenter)

#       Definisco il bottone Firma
        iconsign_file = iconpath+"firma96x96.png"
        self.btn_signFile = QPushButton(QIcon(iconsign_file), '')
        self.btn_signFile.setIconSize(iconsize)
        self.btn_signFile.setFixedSize(btnsize)
        self.btn_signFile.setToolTip("Firma un documento")
        self.btn_signFile.clicked.connect(ActionFunctions.sign_file)

#       Definisco il bottone FirmaCartella
        iconsign_folder = iconpath+"96px-Document-open.svg.png"
        self.btn_signFolder = QPushButton(QIcon(iconsign_folder), '')
        self.btn_signFolder.setFixedSize(btnsize)
        self.btn_signFolder.setIconSize(iconsize)
        self.btn_signFolder.setToolTip("Firma tutti i documenti di una cartella")
        self.btn_signFolder.clicked.connect(ActionFunctions.sign_folder)

#       Definisco il bottone Verifica firma
        iconver_file = iconpath+"verifica96x96.png"
        self.btn_verFile = QPushButton(QIcon(iconver_file), '')
        self.btn_verFile.setIconSize(iconsize)
        self.btn_verFile.setFixedSize(btnsize)
        self.btn_verFile.setToolTip("Verfica la firma di un documento")
        self.btn_verFile.clicked.connect(ActionFunctions.ver_sign_file)

#       Definisco il bottone VerificafirmaCartella
        iconver_folder = ""
        self.btn_ver_folder = QPushButton(QIcon(iconver_folder), 'Verifica c&artella')
        self.btn_ver_folder.setFixedSize(btnsize)
        self.btn_ver_folder.setToolTip("Verifica la firma di tutti i documenti di una cartella")
        self.btn_ver_folder.clicked.connect(ActionFunctions.ver_sign_folder)

#       Definisco il bottone Gestione PIN
        icon_manage_pin = iconpath+"impostazioni96x96.png"
        self.btn_manage_pin = QPushButton(QIcon(icon_manage_pin), '')
        self.btn_manage_pin.setFixedSize(btnsize)
        self.btn_manage_pin.setIconSize(iconsize)
        self.btn_manage_pin.setToolTip("Strumenti: Permette di gestire PIN e PUK\n(Cambio PIN/Sblocco PIN/Cambio PUK)")
        self.btn_manage_pin.clicked.connect(ChangeCodes)
        self.btn_manage_pin.setDisabled(True)

#       Definisco il bottone Riconosci SmartCard
        icon_id_smartcard = iconpath+"smartcardsets96x96.png"
        self.btn_id_smartcard = QPushButton(QIcon(icon_id_smartcard), '')
        self.btn_id_smartcard.setFixedSize(btnsize)
        self.btn_id_smartcard.setIconSize(iconsize)
        self.btn_id_smartcard.setToolTip("Riconosimento del modello di SmartCard")
        self.btn_id_smartcard.clicked.connect(ActionFunctions.get_ATR)
        self.btn_id_smartcard.setDisabled(True)

#       Definisco il bottone Chiudi
        icon_esc = iconpath+"window-close-symbolic.png"
        self.btn_esc = QPushButton('')
        self.btn_esc.setIcon(QIcon(icon_esc))
        self.btn_esc.setIconSize(iconsize)
        self.btn_esc.setFixedSize(btnsize)
        self.btn_esc.setToolTip("Chiude l'applicazione")
        self.btn_esc.clicked.connect(QCoreApplication.instance().quit)

#       Definisco la Drag and Drop area
        self.btn_dnd = LabelDND('Trascina qui per firmare\n(anche cartelle intere)', None)
        self.btn_dnd.setMinimumSize(300, 100)


#       Definisco la label per il log
        self.log_label = QLabel("Area di log:")
        self.log_label.setAlignment(Qt.AlignHCenter)

#       Definisco la log area
        MainWindow.log_area = QTextEdit()
        MainWindow.log_area.setReadOnly(True)
        MainWindow.log_area.setAcceptRichText(True)
        MainWindow.log_area.setMinimumHeight(100)

#       Definisco il layout generale

        self.label_layout = QHBoxLayout()
        self.label_layout.addWidget(self.action_label)

        self.btn_layout_1_row = QHBoxLayout()
        self.btn_layout_1_row.addWidget(self.btn_signFile)
        self.btn_layout_1_row.addWidget(self.btn_signFolder)
        self.btn_layout_1_row.addWidget(self.btn_verFile)

        self.btn_layout_2_row = QHBoxLayout()
#        self.btn_layout_2_row.addWidget(self.btn_ver_folder)
        self.btn_layout_2_row.addWidget(self.btn_manage_pin)
        self.btn_layout_2_row.addWidget(self.btn_id_smartcard)
        self.btn_layout_2_row.addWidget(self.btn_esc)

#        btn_layout_3_row = QHBoxLayout()
#        btn_layout_3_row.addWidget(self.btn_esc)
#        btn_layout_3_row.addWidget(self.btn_esc)
#        btn_layout_3_row.addWidget(self.btn_esc)

        self.log_area_layout = QVBoxLayout()
        self.log_area_layout.addWidget(self.log_label)
        self.log_area_layout.addWidget(self.log_area)

        self.btn_layout_dnd = QHBoxLayout()
        self.btn_layout_dnd.addWidget(self.btn_dnd)

#       Imposta il layout della finestra
        self.main_layout = QGridLayout()
        self.main_layout.addLayout(self.label_layout, 0, 0)
        self.main_layout.addLayout(self.btn_layout_1_row, 1, 0)
        self.main_layout.addLayout(self.btn_layout_2_row, 2, 0)
        #main_layout.addLayout(btn_layout_3_row, 3, 0)
        self.main_layout.addLayout(self.btn_layout_dnd, 4, 0)
        self.main_layout.addLayout(self.log_area_layout, 5, 0)
        self.setLayout(self.main_layout)


    def __init__(self):
        super().__init__()
        self.uicreate()
        DbusCallDaemon.test_connection(self)
