# GUÍA DE SQLALCHEMY PARA PRINCIPIANTES

## ¿QUÉ ES SQLALCHEMY?

SQLAlchemy es una **librería que facilita trabajar con bases de datos** sin escribir SQL puro.

**Sin SQLAlchemy:** 
```sql
INSERT INTO robots (robot_id, timestamp) VALUES ('bot1', '2026-04-11 10:30:00');
```

**Con SQLAlchemy:**
```python
robot = RobotRegistro(robot_id="bot1", timestamp=datetime.now())
session.add(robot)
session.commit()
```

---

## ESTRUCTURA DE UN PROYECTO CON SQLALCHEMY

### 1. Importar librerías
```python
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
```

### 2. Crear la base
```python
Base = declarative_base()
```
Una sola vez al inicio. Es la base para todos tus modelos.

### 3. Definir los modelos
```python
class RobotRegistro(Base):
    __tablename__ = "robots"  # nombre de la tabla
    
    id = Column(Integer, primary_key=True)
    robot_id = Column(String)
    timestamp = Column(DateTime)
```

### 4. Crear conexión y tablas
```python
engine = create_engine("sqlite:///data/robots.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
```

### 5. Usar sesiones
```python
session = Session()
# ... hacer cosas ...
session.close()
```

---

## LOS 4 PASOS PARA CUALQUIER OPERACIÓN

### PASO 1: Crear sesión
```python
session = Session()
```

### PASO 2: Hacer la operación
```python
# Crear
robot = RobotRegistro(robot_id="bot1", timestamp=datetime.now())
session.add(robot)

# O leer
robot = session.query(RobotRegistro).first()

# O actualizar
robot.timestamp = datetime.now()

# O eliminar
session.delete(robot)
```

### PASO 3: Guardar cambios
```python
session.commit()
```

### PASO 4: Cerrar sesión
```python
session.close()
```

---

## OPERACIONES BÁSICAS

### CREATE (CREAR)
```python
session = Session()

robot = RobotRegistro(robot_id="bot1", timestamp=datetime.now())
session.add(robot)
session.commit()

session.close()
```

### READ (LEER)
```python
session = Session()

# Obtener todos
todos = session.query(RobotRegistro).all()

# Obtener el primero que cumpla condición
uno = session.query(RobotRegistro).filter_by(robot_id="bot1").first()

session.close()
```

### UPDATE (ACTUALIZAR)
```python
session = Session()

robot = session.query(RobotRegistro).filter_by(robot_id="bot1").first()

if robot:
    robot.timestamp = datetime.now()
    session.commit()

session.close()
```

### DELETE (ELIMINAR)
```python
session = Session()

robot = session.query(RobotRegistro).filter_by(robot_id="bot1").first()

if robot:
    session.delete(robot)
    session.commit()

session.close()
```

---

## TIPOS DE DATOS

| Python | SQLAlchemy | Ejemplo |
|--------|-----------|---------|
| número | `Integer` | `42` |
| texto | `String` | `"robot_001"` |
| fecha | `DateTime` | `datetime.now()` |

---

## ERRORES COMUNES

❌ **Olvidar `commit()`**
```python
session.add(robot)
# SIN session.commit() <- NO se guarda en la BD!
```

❌ **Olvidar `close()`**
```python
session = Session()
# ... código ...
# SIN session.close() <- Recurso abierto innecesariamente
```

❌ **No comprobar si existe**
```python
robot = session.query(RobotRegistro).filter_by(robot_id="X").first()
print(robot.timestamp)  # ERROR si no existe (None)
```

✅ **CORRECTO**
```python
robot = session.query(RobotRegistro).filter_by(robot_id="X").first()
if robot:
    print(robot.timestamp)
```

---

## FLUJO COMPLETO

```python
# Conexión (una sola vez)
engine = create_engine("sqlite:///robots.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Usar (cada vez que necesites)
session = Session()
try:
    # Tu código aquí
    robot = RobotRegistro(robot_id="bot1")
    session.add(robot)
    session.commit()
finally:
    session.close()
```

---

## PRÓXIMOS PASOS

1. Lee el archivo `clases.py` para ver el código real
2. Ejecuta `ejemplos_sqlalchemy.py` para ver cómo funciona
3. Modifica los ejemplos y experimenta
4. Añade más columnas al modelo si necesitas guardar más datos
