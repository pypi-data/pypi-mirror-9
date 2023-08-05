class usrconfig():
    def __init__(self, archivo):
        f = open(archivo, 'r')
        lineas = f.readlines()
        f.close()
        l = []
        self.d = {}
        for linea in lineas:
            linea = linea.replace("\n", "")
            linea = linea.replace("\r", "")
            if linea.find("#") == -1:
                pass
            else:
                n = linea.find("#")
                linea = linea[:n]
            if linea:
                l.append(linea)
        for valor in l:
            valor = valor.replace(" ", "")
            comp = valor.split("=")
            self.d[comp[0]] = comp[1]
    def get_value(self, value):
        if value in self.d:
            return self.d[value]
        else:
            return None