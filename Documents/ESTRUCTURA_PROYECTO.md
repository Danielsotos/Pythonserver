# ESTRUCTURA DEL PROYECTO - GUÍA PARA PRINCIPIANTES

## 📁 Carpetas y archivos principales

```
Pythonserver/
├── clases.py           ← Gestión de la base de datos
├── controladores.py    ← Rutas de la API (GET, POST)
├── main.py            ← Archivo principal que inicia el servidor
├── logger.py          ← Configuración de logs
├── requirements.txt   ← Librerías necesarias
├── Dockerfile         ← Para ejecutar en contenedor
├── templates/         ← Páginas HTML
│   ├── index.html
│   ├── FLR.html
│   └── SBS.html
├── static/            ← Archivos CSS y JS
│   ├── app.js
│   └── style.css
├── pictures/          ← Imágenes
└── data/              ← Base de datos (se crea automáticamente)
    └── robots.db
```

---

## 🔄 FLUJO DEL PROYECTO

```
Usuario (Frontend)
    ↓
app.js (envía solicitud)
    ↓
FastAPI (main.py)
    ↓
RobotAPI (controladores.py)  ← Procesa la solicitud
    ↓
RobotDataManager (clases.py) ← Maneja la base de datos
    ↓
SQLAlchemy
    ↓
Base de datos SQLite
```

---

## 📝 EXPLICACIÓN DE CADA ARCHIVO

### 1. **clases.py** - La base de datos
```python
class RobotRegistro(Base):
    # Tabla con columnas: id, section, robot_id, timestamp
```

**Qué hace:**
- Define cómo se ve la tabla de robots
- Tiene métodos para crear, leer, actualizar y eliminar robots

**Métodos principales:**
- `add_robot(section, robot_id)` - Crear un robot
- `get_all()` - Obtener todos los robots
- `get_robot(robot_id)` - Buscar un robot específico
- `update_robot(robot_id)` - Actualizar timestamp
- `delete_robot(robot_id)` - Eliminar un robot

### 2. **controladores.py** - Las rutas de la API
```python
class RobotAPI:
    def guardar_flr(self, robot: RobotRequest):
        # Guardar robot en sección FLR
```

**Qué hace:**
- Define las rutas HTTP (GET, POST)
- Conecta el frontend con la base de datos

**Rutas disponibles:**
- `GET /` - Mostrar página principal
- `GET /FLR` - Mostrar página FLR
- `GET /SBS` - Mostrar página SBS
- `GET /datos` - Obtener todos los datos JSON
- `POST /FLR` - Guardar robot en FLR
- `POST /SBS` - Guardar robot en SBS

### 3. **main.py** - Inicia el servidor
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Qué hace:**
- Crea la aplicación FastAPI
- Conecta las rutas
- Inicia el servidor en puerto 8080

### 4. **logger.py** - Registra lo que pasa
```python
logger.info("POST /FLR - robot_id=%s", robot.id)
```

**Qué hace:**
- Guarda en `logs.log` lo que sucede
- Muestra mensajes en la consola

---

## 🚀 CÓMO USAR EL PROYECTO

### Inicio del servidor
```bash
python main.py
```

El servidor estará en: `http://localhost:8080`

### Ver datos en JSON
```
GET http://localhost:8080/datos
```

Respuesta:
```json
{
  "robotsFLR": [
    {"id": "robot_001", "timestamp": "2026-04-11 10:30:00"}
  ],
  "robotsSBS": [
    {"id": "robot_002", "timestamp": "2026-04-11 10:35:00"}
  ]
}
```

### Crear un robot (desde JavaScript)
```javascript
fetch('/FLR', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: 'robot_003'})
})
```

---

## 📊 CICLO COMPLETO: GUARDAR UN ROBOT

### 1. Frontend (app.js)
```javascript
// Usuario envía solicitud
fetch('/FLR', {method: 'POST', body: ...})
```

### 2. API (controladores.py)
```python
def guardar_flr(self, robot: RobotRequest):
    # Recibe el robot
    self.data_manager.add_robot("robotsFLR", robot.id)
    # Retorna confirmación
```

### 3. Base de datos (clases.py)
```python
def add_robot(self, section, robot_id):
    # Crea sesión
    session = self.Session()
    
    # Crea registro
    nuevo_robot = RobotRegistro(...)
    
    # Guarda en BD
    session.add(nuevo_robot)
    session.commit()
    session.close()
```

### 4. SQLite
```
Tabla robots:
| id | section   | robot_id   | timestamp        |
|----|-----------|------------|------------------|
| 1  | robotsFLR | robot_003  | 2026-04-11 10:30 |
```

---

## 🔍 FLUJO DE LECTURA: OBTENER DATOS

### 1. Frontend pide datos
```javascript
fetch('/datos')
```

### 2. API recibe solicitud
```python
def datos(self):
    datos = self.data_manager.get_all()
    return JSONResponse(content=datos)
```

### 3. Base de datos busca
```python
def get_all(self):
    robots = session.query(RobotRegistro).all()
    # Organiza por sección
    # Retorna diccionario
```

### 4. Frontend recibe JSON
```json
{"robotsFLR": [...], "robotsSBS": [...]}
```

---

## 📚 CONCEPTOS CLAVE

| Concepto | Qué es |
|----------|---------|
| **FastAPI** | Framework web (crea la API) |
| **Uvicorn** | Servidor que ejecuta FastAPI |
| **SQLAlchemy** | Librería para usar base de datos |
| **SQLite** | Base de datos (archivo `robots.db`) |
| **Router** | Define las rutas (GET, POST, etc) |
| **Session** | Conexión con la BD para hacer cambios |
| **Pydantic** | Valida datos que recibe la API |

---

## ⚙️ CÓMO FUNCIONA UNA SOLICITUD HTTP

### Solicitud GET
```
Navegador envía: GET /FLR
↓
FastAPI recibe la solicitud
↓
controladores.py → def flr(self)
↓
Retorna: FileResponse("templates/FLR.html")
↓
Navegador muestra la página
```

### Solicitud POST
```
app.js envía: POST /FLR {id: "robot_001"}
↓
FastAPI recibe la solicitud
↓
controladores.py → def guardar_flr(self, robot)
↓
clases.py → data_manager.add_robot("robotsFLR", "robot_001")
↓
SQLite guarda el robot
↓
Retorna: {"message": "Datos guardados correctamente", ...}
↓
app.js recibe la respuesta
```

---

## 🐛 DEBUGGING

### Ver logs en tiempo real
```bash
tail -f logs.log
```

### Ver que está guardando
```
GET http://localhost:8080/datos
```

### Verificar base de datos
```bash
sqlite3 data/robots.db
sqlite> SELECT * FROM robots;
```

---

## 📌 RESUMEN

1. **clases.py** = Gestión de la BD
2. **controladores.py** = Rutas de la API
3. **main.py** = Inicia todo
4. **logger.py** = Registra eventos
5. **templates/** = Frontend HTML
6. **static/** = CSS y JavaScript

**El flujo es simple:**
Cliente Frontend → API (FastAPI) → Base de Datos (SQLite)
