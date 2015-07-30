#!/usr/bin/python3
# coding=utf-8

# Dbus experimental test. this file has to be deleted when tests are over.

from PyQt5.Qt import QDBusInterface
from PyQt5.Qt import QDBusReply

class DbusTokenManagerCallDaemon(object):
    service = "it.libersoft.firmapiud.dbusinterface.TokenManagerInterface"
    path = "/it/libersoft/firmapiud/TokenManager"
    interface = "it.libersoft.firmapiud.dbusinterface.TokenManagerInterface"

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

    def verifyPin(self,pin):
        return self.__verifyPinPuk("verifyPin", pin)
    
    def verifyPuk(self,puk):
        return self.__verifyPinPuk("verifyPuk", puk)
    
    def getPinRemainingAttempts(self):
        return self.__pinPukRemainingAttempts("getPinRemainingAttempts")
    
    def getPukRemainingAttempts(self):
        return self.__pinPukRemainingAttempts("getPukRemainingAttempts")
    
    def unlockPKCS11Token(self,puk,newPin):
        return self.__setPinPukProcedure("unlockPKCS11Token", puk, newPin)
    
    def __checkPin(self, pin):
        length = len(pin)
        if not(pin.isnumeric() and length >= 5 and length <= 8):
            raise Exception(
                            "codice non valido!", 
                            "Il pin/puk immesso deve contenere solo numeri ed essere compreso tra 5 e 8 caratteri")    

    def __setPinPukProcedure(self,operation,oldPin,newPin):
        self.__checkPin(oldPin)
        self.__checkPin(newPin)
        result = self.fpiudaemon.call(operation, oldPin, newPin)
        return self.__replyVoidProcedure(result)
    
    def __verifyPinPuk(self,operation,pin):
        self.__checkPin(pin)
        result = self.fpiudaemon.call(operation, pin)
        return self.__replyResultProcedure(result)

    def __pinPukRemainingAttempts(self,operation):
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
        
token = DbusTokenManagerCallDaemon()
token.setPin("87654321", "12345678")
token.setPin("12345678","87654321")
token.setPuk("87654321", "12345678")
token.setPuk("12345678","87654321")
print (token.verifyPin("87654321"))
print (token.verifyPuk("87654321"))
print ("Tentativi rimasti pin %i" % token.getPinRemainingAttempts())
print ("Tentativi rimasti puk %i" % token.getPukRemainingAttempts())

try:
    print (token.verifyPin("8765432"))
except Exception as err:
    print (format(err))

try:
    print (token.verifyPuk("8765432"))
except Exception as err:
    print (format(err))

print ("Tentativi rimasti pin %i" % token.getPinRemainingAttempts())
print ("Tentativi rimasti puk %i" % token.getPukRemainingAttempts())

print (token.verifyPin("87654321"))
print (token.verifyPuk("87654321"))
print ("Tentativi rimasti pin %i" % token.getPinRemainingAttempts())
print ("Tentativi rimasti puk %i" % token.getPukRemainingAttempts())

try:
    print (token.verifyPin("8765432"))
except Exception as err:
    print (format(err))

try:
    print (token.verifyPin("8765432"))
except Exception as err:
    print (format(err))

try:
    print (token.verifyPin("8765432"))
except Exception as err:
    print (format(err))

try:
    print (token.verifyPin("8765432"))
except Exception as err:
    print (format(err))
    
token.unlockPKCS11Token("87654321", "87654321")
print (token.verifyPin("87654321"))