import logging

#logging.getLogger("uvicorn.access").disabled = True # Desactiva los logs de acceso de Uvicorn para evitar que se mezclen con los logs personalizados de la aplicación, lo que ayuda a mantener los registros más limpios y enfocados en las operaciones específicas de la API de robots.
logging.getLogger("uvicorn.access").setLevel(logging.ERROR) # Configura el nivel de logueo para los logs de acceso de Uvicorn a ERROR, lo que significa que solo se registrarán los errores graves relacionados con las solicitudes HTTP, mientras que los mensajes informativos y de depuración no se mostrarán en los logs de acceso. Esto ayuda a reducir el ruido en los registros y a centrarse en los problemas importantes.

logger = logging.getLogger("robot_api") # Crea un logger específico para la API de robots, lo que permite registrar mensajes relacionados con las operaciones de la API de manera organizada y diferenciada de otros loggers en la aplicación
logger.setLevel(logging.DEBUG) # Configura el nivel de logueo a DEBUG para registrar mensajes detallados para depuración

format = logging.Formatter("%(levelname)s:     %(asctime)s %(message)s")

console= logging.StreamHandler()
console.setLevel(logging.INFO) # Configura el nivel de logueo a INFO para la consola, para mostrar solo mensajes informativos y superiores en la salida estándar
console.setFormatter(format)

file = logging.FileHandler("logs.log", encoding="utf-8")
file.setLevel(logging.DEBUG) # Configura el nivel de logueo a DEBUG para el archivo, para registrar mensajes detallados para depuración en el archivo de log
file.setFormatter(format)

logger.addHandler(console) # Agrega el handler de consola al logger para que los mensajes se muestren en la salida estándar
logger.addHandler(file) # Agrega el handler de archivo al logger para que los mensajes se registren en el archivo "logs.log"


