import crypto
import os.path
class config():
    def __init__(self, archivo, encryption):
        if(encryption):
            self.encryption = True
            self.archivo = archivo
            self.passwd = "ShR0hv71" #salt comuna
        else:
            self.encryption = False
            self.archivo = archivo
        self.opciones = {}
    def load(self):
        archivo = self.archivo
        if not os.path.isfile(archivo):
            f = open(archivo, "w")
            f.close()
        if(self.encryption):
            crypto.desencriptar(self.archivo, self.passwd)
            f = open(self.archivo, "r")
            self.txt = f.read()
            f.close()
            crypto.encriptar(self.archivo, self.passwd)
        else:
            f = open(self.archivo, "r")
            self.txt = f.read()
            f.close()
        #carga, <--new-!>hola<--set-!>bye
        self.txt = self.txt.split("<--new-!>")
        v1 = ""
        for i in self.txt:
            if i == "":
                continue
            v1 = i.split("<--set-!>")
            self.opciones[v1[0]] = v1[1]
    def get_value(self, variable):
        try:
            return self.opciones[variable]
        except KeyError:
            return None
    def set_value(self, variable, valor):
        self.opciones[variable] = valor
        return self.opciones[variable]
    def save(self):
        keys = self.opciones.keys()
        txt = ""; txt_1 = ""
        for i in range(len(self.opciones)):
            variable = keys[i]
            valor = self.opciones[keys[i]]
            txt_1 = "<--new-!>%s<--set-!>%s" % (variable, valor)
            txt = txt + txt_1
        f = open(self.archivo, "w")
        f.write(txt)
        f.close()
        if(self.encryption):
            crypto.encriptar(self.archivo, self.passwd)