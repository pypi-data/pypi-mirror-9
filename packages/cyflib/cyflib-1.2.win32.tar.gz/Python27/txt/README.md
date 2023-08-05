======
CyfLib
======

CyfLib es una librería de código abierto para python. Lo que se pretende con esta librería es facilitar la escritura del código en Python y añadir funciones adicionales. Información completa: http://cyflib.cu.cc

Clases
======

* **ProgressBar**. Construcción de barras de progreso mostradas en consola.

* **BitCoin**. Funciones relacionadas con BitCoin. No permite enviar BitCoins.

* **ConfigManager**. Creación de archivos de configuración de manera fácil.

* **RSA**. Sistema de criptografia asimétrica RSA: cifrado, descifrado y firma.

* **SQL**. Permite usar SQLLite de una manera sencilla. 

Información de las clases
-------------------------

Puedes encontrar más información en http://cyfnet.com/cyflib


ProgressBar
------------

La clase ProgressBar() de CyfLib permite crear barras de progreso fácilmente. Estas barras son altamente personalizables vía **kwargs.

1. Se personaliza la barra con **kwargs. Se crea un diccionario que puede contener los siguientes valores:

* str "char_full" - Carácter de la barra llena.

* str "char_empty" - Carácter de la barra vacía.

* int "width" - Anchura de la barra.

* bool "percentage" - Mostrar porcentaje al lado de la barra. 

Ejemplo: personalizacion = {"char_full":"/", "char_empty":" ", "width":30, "percentage":True}

2. Se crea la barra. **kwargs es opcional (se requiere ** para especificar que se trata de kwargs)

p = cyflib.ProgressBar(**personalizacio)

3. La barra ya está creada (No se muestra nada en pantalla).

* p.Update() - Muestra la barra de progreso. Si no se ha imprimido nada más en la consola, la barra solo se imprimirá una vez, actualizandóse.

* p.Update(msg) - Muestra la barra de progreso, junto a un mensaje (msg)

* p.Increment(int) - Se incremente el porcentaje. El valor se suma al que había anteriormente. No admite coma flotante. 

* p.Reset() - Resetea el porcentaje a 0.

* p.Percentage() - Devuelve el porcentaje de la barra.

* p.PrintBar() - Imprime la barra en pantala sin usar sys.stdout(), eso significa que la barra no aparecerá en la misma línea.


BitCoin
---------

La clase BitCoin() de CyfLib usa funciones relacionadas con BitCoin: Crear claves, comprobar saldo de una dirección pública y transformar claves privadas a públicas.

btc = cyflib.BitCoin()

Luego, se pueden usar las diferentes funciones:

* GetAddress(semilla) Crea una dirección de monedero BitCoin a partir de una semilla.

* GetPrivateKey(semilla) Crea una clave privada de BitCoin a partir de una semilla.

* CheckBalance(direccion) Comprueba el saldo de una dirección BitCoin usando la API de BlockChain. Se requiere una conexión a Internet.

* ConvertAmount(cantidad) Transforma la cantidad devuelta por CheckBalance() a BTC.

* AddressByPrivateKey(clave_privada) Genera una dirección de monedero BitCoin a partir de una clave privada. Si es la misma clave privada, la dirección siempre será la misma.

* RandomSeed() Genera una semilla aleatoria segura para usarla para crear claves privadas, usando: key = btc.GetPrivateKey(btc.RandomSeed()).


ConfigManager
-------------

Esta clase permite crear un archivo de configuración de manera sencilla. 

a = cyflib.ConfigManager(archivo, encriptacion)
#archivo = el archivo de configuracion
#encriptacion = por defecto True, cifra el archivo para evitar modificaciones.

Funciones de ConfigManager:

* a.Create() - Crea el archivo de configuración, si existe se sobrescribe.

* a.Load() - Carga el archivo.

* a.SetValue(variable, valor) - Establece una variable con un valor

* a.GetValue(variable) - Devuelve el valor de variable

* a.Save() - Guarda el archivo. Una vez guardado se deberá cargar de nuevo.

RSA
---

Esta clase sirve para usar RSA. CyfLib es capaz de firmar, encriptar y desencriptar mensajes usando la criptografía asimétrica. Las claves producidas y los mensajes encriptados son vueltos a encriptar usando BASE64. El cifrado RSA implementado en CyfLib esta bajo fase beta y no debería ser usado para mensajes importantes, aunque es muy seguro. Para usar RSA primero debemos importar la clase:

a = cyflib.RSA()

Y ahora podemos usar las siguientes funciones:

* a.Generar_claves(n) Genera claves con "n" bits. El número por defecto es 512 bits. Cuantos más bits, más segura pero más lenta será la clave, y obviamente podrá encriptar mensajes más grandes. Devuelve una tupla del tipo: (clave_publica, clave_privada). Por eso se debe usar así:
    publica, privada = a.Generar_claves(n)
    
* a.Encriptar(mensaje, clave_publica) Encripta un mensaje usando una clave publica. Si el mensaje es muy largo el algoritmo falla, todo depende de los bits de las claves.

* a.Desencriptar(mensaje_encriptado, clave_privada, clave_publica) Desencripta el mensaje usando la clave privada y la clave publica.

* a.Firmar(mensaje, clave_privada, clave_publica) Devuelve una firma. Esto sirve para controlar que el mensaje no se ha modificado por el camino y que lo ha emitido el emisor original.

* a.Comprobar_firma(mensaje, firma, clave_publica) Comprueba una firma, usando la clave publica del emisor que ha firmado el mensaje.


SQL
---

Con esta clase se puede usar SQL de una manera sencilla.

a = cyflib.SQL(database) 

Dónde database es el nombre del archivo. No se cargará ningún archivo hasta que llamemos a la función Load(). Listado de funciones:

* a.Load() Carga la base de datos, si no existe se crea.

* a.Query(consulta) Ejecuta la consulta en lenguaje SQL.

* a.Save() Guarda los datos en la base de datos, se debe hacer antes de la función Close(). Dependiendo de la versión de SQLLite y de Python no hará falta.

* a.FetchAll() Devuelve el FetchAll de una consulta.

* a.Close() Cierra la base de datos.

Fin de las funciones de CyfLib, ejemplos en http://cyflib.cu.cc
