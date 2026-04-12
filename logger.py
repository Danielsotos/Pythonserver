import logging

# Configurar nivel de logs de Uvicorn
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

# Crear un logger específico para nuestra API
logger = logging.getLogger("robot_api")
logger.setLevel(logging.DEBUG)

# Formato de los logs
formato = logging.Formatter("%(levelname)s:     %(asctime)s %(message)s")

# Handler para mostrar logs en la consola
consola = logging.StreamHandler()
consola.setLevel(logging.INFO)
consola.setFormatter(formato)

# Handler para guardar logs en archivo
archivo = logging.FileHandler("logs.log", encoding="utf-8")
archivo.setLevel(logging.DEBUG)
archivo.setFormatter(formato)

# Agregar handlers al logger
logger.addHandler(consola)
logger.addHandler(archivo)


