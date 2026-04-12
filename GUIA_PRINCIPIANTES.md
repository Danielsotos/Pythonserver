# GUÍA PARA PRINCIPIANTES - CONSEJOS Y BUENAS PRÁCTICAS

## 1. ANTES DE EMPEZAR

### Requisitos previos que debes entender
- ✅ Conocer Python básico (variables, funciones, clases)
- ✅ Saber qué es una base de datos
- ✅ Entender peticiones HTTP (GET, POST)
- ✅ Conocer JavaScript básico (para el frontend)

### Si no entiendes algo
1. **Lee el código línea por línea**
2. **Busca en Google + "python" o "fastapi"**
3. **Ejecuta experimentos pequeños en `ejemplos_sqlalchemy.py`**

---

## 2. ESTRUCTURA DE UNA SOLICITUD HTTP

### Solicitud GET (pedir datos)
```
GET /FLR
↓
"Oye servidor, muéstrame la página FLR"
↓
Servidor: "Aquí está el archivo FLR.html"
```

### Solicitud POST (enviar datos)
```
POST /FLR
Body: {"id": "robot_001"}
↓
"Oye servidor, guarda este robot en la sección FLR"
↓
Servidor: "Listo, lo guardé en la base de datos"
```

---

## 3. CÓMO LEER EL CÓDIGO

### Paso 1: main.py
```python
uvicorn.run(app, host="0.0.0.0", port=8080)
```
💡 **Qué pasa:** Inicia el servidor en el puerto 8080

### Paso 2: Llega una solicitud
El cliente envía: `POST /FLR {"id": "robot_001"}`

### Paso 3: controladores.py (RobotAPI)
```python
def guardar_flr(self, robot: RobotRequest):
    logger.info("POST /FLR - robot_id=%s", robot.id)
    self.data_manager.add_robot("robotsFLR", robot.id)
    return {"message": "Datos guardados..."}
```
💡 **Qué pasa:** Recibe la solicitud y guarda el robot

### Paso 4: clases.py (RobotDataManager)
```python
def add_robot(self, section, robot_id):
    # Crea una conexión (sesión)
    session = self.Session()
    
    # Crea el objeto
    nuevo_robot = RobotRegistro(...)
    
    # Lo guarda
    session.add(nuevo_robot)
    session.commit()
    session.close()
```
💡 **Qué pasa:** Guarda en la base de datos

### Paso 5: Base de datos
```
SQLite guarda:
| id | section   | robot_id | timestamp      |
|----|-----------|----------|----------------|
| 1  | robotsFLR | robot_001| 2026-04-11 ... |
```

---

## 4. CONCEPTO: SESSION (SESIÓN)

Una sesión es como una **conversación con la base de datos**:

```python
# 1. Iniciar conversación
session = self.Session()

# 2. Hacer cosas (add, update, delete)
session.add(nuevo_robot)

# 3. Confirmar cambios
session.commit()

# 4. Finalizar conversación
session.close()
```

### ⚠️ IMPORTANTE
- Sin `commit()` → Los cambios NO se guardan
- Sin `close()` → La conexión queda abierta

---

## 5. CONCEPTO: MODEL (MODELO)

Un modelo es una **plantilla** de cómo se ve la tabla:

```python
class RobotRegistro(Base):
    __tablename__ = "robots"
    
    id = Column(Integer, primary_key=True)
    section = Column(String)
    robot_id = Column(String)
    timestamp = Column(DateTime)
```

💡 Esto le dice a SQLAlchemy: "La tabla tiene 4 columnas"

---

## 6. TIPOS DE COLUMNAS

| Tipo | Python | Ejemplo |
|------|--------|---------|
| Número | `Integer` | `42`, `1` |
| Texto | `String` | `"robot_001"`, `"robotsFLR"` |
| Fecha | `DateTime` | `2026-04-11 10:30:00` |
| Booleano | `Boolean` | `True`, `False` |
| Decimal | `Float` | `3.14`, `99.99` |

---

## 7. QUERY (CONSULTAS)

### Obtener todos
```python
robots = session.query(RobotRegistro).all()
# Retorna: [robot1, robot2, robot3, ...]
```

### Obtener el primero que cumple condición
```python
robot = session.query(RobotRegistro).filter_by(robot_id="robot_001").first()
# Retorna: robot1 (o None si no existe)
```

### Contar
```python
total = session.query(RobotRegistro).count()
# Retorna: 42
```

---

## 8. MANEJO DE ERRORES BÁSICO

### SIN manejo de errores (❌ MALO)
```python
def add_robot(self, section, robot_id):
    session = self.Session()
    robot = RobotRegistro(section=section, robot_id=robot_id)
    session.add(robot)
    session.commit()  # ¿Y si falla? ¿Cómo lo supo?
    session.close()
```

### CON manejo básico (✅ MEJOR)
```python
def add_robot(self, section, robot_id):
    session = self.Session()
    try:
        robot = RobotRegistro(section=section, robot_id=robot_id)
        session.add(robot)
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()  # Siempre se cierra
```

---

## 9. ROUTERS EN FASTAPI

### Definir una ruta
```python
@app.get("/FLR")  # Ruta GET
def flr():
    # Código aquí
```

### En nuestro proyecto (sin decoradores)
```python
self.router.add_api_route("/FLR", self.flr, methods=["GET"])
```

Es lo mismo pero escrito diferente.

---

## 10. PYDANTIC (VALIDAR DATOS)

### Sin Pydantic (❌ PELIGROSO)
```python
def guardar_flr(data):
    # ¿Qué pasa si data no tiene "id"?
    # ¿Qué pasa si id es un número?
    robot_id = data["id"]
```

### Con Pydantic (✅ SEGURO)
```python
class RobotRequest(BaseModel):
    id: str  # FastAPI valida que sea texto

def guardar_flr(self, robot: RobotRequest):
    # Aquí ya sé que robot.id es texto
```

---

## 11. LOGGER (REGISTRAR EVENTOS)

### Qué es
Es como un "diario" de lo que pasa en tu app

### Cómo usarlo
```python
logger.info("Se guardó robot: %s", robot_id)
```

### Dónde se guarda
- **Consola:** Se ve en tiempo real
- **Archivo:** `logs.log` (para investigar después)

### Niveles
| Nivel | Uso |
|-------|-----|
| DEBUG | Información detallada (desarrollo) |
| INFO | Eventos normales |
| ERROR | Algo salió mal |
| WARNING | Algo que podría ser problema |

---

## 12. CICLO COMPLETO: DEPURACIÓN

### Problema: "El robot no se está guardando"

**Paso 1:** Ver logs
```bash
tail -f logs.log
```

**Paso 2:** Ver base de datos
```bash
sqlite3 data/robots.db
sqlite> SELECT * FROM robots;
```

**Paso 3:** Comprobar que llega la solicitud
```bash
# Prueba en JavaScript console
fetch('/FLR', {method: 'POST', body: JSON.stringify({id: 'test'})})
```

**Paso 4:** Verificar el código
```python
def guardar_flr(self, robot: RobotRequest):
    print(f"Debug: recibí {robot.id}")  # Agregar este print
    self.data_manager.add_robot("robotsFLR", robot.id)
```

---

## 13. CHECKLIST PARA ANTES DE COMMITAR

- [ ] El código funciona sin errores
- [ ] No hay variables sin usar
- [ ] Los nombres de variables son claros
- [ ] Hay comentarios en partes confusas
- [ ] Los logs son útiles (no sólo vacíos)
- [ ] Probé casos de error

---

## 14. ERRORES COMUNES

### Error 1: "AttributeError: 'NoneType' object has no attribute"
```python
robot = session.query(...).first()
print(robot.timestamp)  # ❌ ERROR si robot es None
```

**Solución:**
```python
if robot:
    print(robot.timestamp)  # ✅ Correcto
```

### Error 2: "La BD no tiene datos pero yo creé robots"
```python
session.add(robot)  # Agregué
# Pero olvidé session.commit()
session.close()
```

**Solución:** Siempre haz `commit()`

### Error 3: "No se cierra la sesión"
```python
session = self.Session()
doing_something()  # Si esto falla...
session.close()  # ... nunca se ejecuta
```

**Solución:** Usa `try/finally`
```python
session = self.Session()
try:
    doing_something()
finally:
    session.close()  # Siempre se ejecuta
```

---

## 15. PRÓXIMOS PASOS PARA APRENDER

1. **Ejecuta los ejemplos** en `ejemplos_sqlalchemy.py`
2. **Modifica el código** y ve qué pasa
3. **Lee la documentación**:
   - FastAPI: https://fastapi.tiangolo.com
   - SQLAlchemy: https://docs.sqlalchemy.org
4. **Crea nuevas rutas** personalizadas
5. **Añade más columnas** a la tabla

---

## 16. PREGUNTAS FRECUENTES

### ¿Dónde se guardan los datos?
En `data/robots.db` (archivo SQLite)

### ¿Cómo vacío la base de datos?
```bash
rm data/robots.db
# Se crea una nueva la próxima vez que inicia
```

### ¿Cómo veo los datos guardados?
```
GET http://localhost:8080/datos
```

### ¿Cómo pruebo sin frontend?
Usa **Postman** o **Insomnia** (herramientas gráficas para API)

### ¿Puedo cambiar el puerto?
```python
# En main.py
uvicorn.run(app, host="0.0.0.0", port=3000)  # Cambiar 8080
```

---

## 🎯 RECUERDA

> "El mejor código es el que se entiende fácilmente
> Mejor un código simple que un código complicado y rápido"

- Escribe comentarios claros
- Usa nombres descriptivos
- Prueba tu código
- No tengas miedo de romper cosas (así aprendes)
