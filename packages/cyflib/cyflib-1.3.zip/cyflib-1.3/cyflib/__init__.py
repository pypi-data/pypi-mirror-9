import password
class ProgressBar():
    def __init__(self, **kwargs):
        import progressbar as pb
        self.progressbarvar = pb.progressbar(**kwargs)
        return None
    def Update(self, message=None):
        """Se actualiza la barra de progreso"""
        self.progressbarvar.print_progress_bar(message)
    def Increment(self, incremento):
        """Incrementar el porcentaje"""
        self.progressbarvar.increment(incremento)
    def Reset(self):
        """Reiniciar la barra de progreso"""
        self.progressbarvar.progress = 0
    def Percentage(self):
        """Devuelve --> int(porcentaje)"""
        return self.progressbarvar.progress
    def PrintBar(self):
        return self.progressbarvar.return_barra()

class BitCoin():
    def __init__(self):
        import bitcoin as btc
        self.bitcoin = btc.BitCoin()
        return None
    def GetAddress(self, seed):
        """Devuelve --> str(direccion_publica)"""
        return self.bitcoin.GetAddress(seed)
    def GetPrivateKey(self, seed):
        """Devuelve --> str(clave_privada)"""
        return self.bitcoin.GetPrivKey(seed)
    def CheckBalance(self, address):
        """Devuelve --> str(saldo)"""
        return self.bitcoin.CheckBalance(address)
    def ConvertAmount(self, decimal):
        """Devuelve --> str(saldo)"""
        return self.bitcoin.TransformBTC(decimal)
    def AddressByPrivateKey(self, privatekey):
        """Devuelve --> str(direccion_publica)"""
        return self.bitcoin.AddressByPrivateKey(privatekey)
    def RandomSeed(self):
        """Devuelve --> str(semilla_aleatoria)"""
        return self.bitcoin.RandomSeed()

class DataBase():
    def __init__(self, archivo, encryption=True):
        import database
        self.cfgm = database.config(archivo, encryption)
        return None
    def Load(self):
        """Carga el archivo de configuracion, si no existe se crea"""
        return self.cfgm.load()
    def Save(self):
        """Guarda el archivo de configuracion"""
        self.cfgm.save()
        self.cfgm.load()
        return None
    def GetValue(self, variable):
        """Devuelve --> str(valor)"""
        return self.cfgm.get_value(variable)
    def SetValue(self, variable, valor):
        """Establece un valor a una variable"""
        return self.cfgm.set_value(variable, valor)

class UserConfig():
    def __init__(self, archivo):
        import usrconfig
        self.uc = usrconfig.usrconfig(archivo)
        return None
    def GetValue(self, variable):
        """Devuelve el valor del archivo"""
        return self.uc.get_value(variable)

class RSA():
    def __init__(self):
        import rsa_def
        return None
    def GenerateKeys(self, bits=512): #Devuelve (clave_publica, clave_privada)
        """Devuelve --> tuple(clave_publica, clave_privada)"""
        return rsa_def.generar_claves(bits)
    def Crypt(self, mensaje, clave_publica):
        """Cifra un mensaje con la clave publica del receptor"""
        return rsa_def.encriptar(mensaje, clave_publica)
    def Decrypt(self, mensaje_encriptado, clave_privada, clave_publica):
        """Descifra el mensaje"""
        return rsa_def.desencriptar(mensaje_encriptado, clave_privada, clave_publica)
    def Sign(self, mensaje, clave_privada, clave_publica):
        """Firma el mensaje"""
        return rsa_def.sign(mensaje, clave_privada, clave_publica)
    def CheckSign(self, mensaje, firma, clave_publica):
        """Comprueba la autenticidad del mensaje"""
        return rsa_def.checksign(mensaje, firma, clave_publica)
       
class SQL():
    def __init__(self, database):
        import cyfsql
        self.sqllite = cyfsql.CyfSQL(database)
    def Load(self):
        return self.sqllite.load()
    def Save(self):
        return self.sqllite.save()
    def Close(self):
        return self.sqllite.close()
    def Query(self, query):
        return self.sqllite.query(query)
    def FetchAll(self):
        return self.sqllite.fetchall()

def GetPassword(prompt = ""):
    return password.getpassword(prompt)
__name__ = "CyfLib"
__version__ = "1.3"