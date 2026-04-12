"""
EJEMPLOS DE USO DE SQLALCHEMY - BÁSICO
======================================
"""

from clases import RobotDataManager

# Crear el gestor de base de datos
manager = RobotDataManager("data/robots.db")

# ========== 1. CREAR (CREATE) ==========
print("=== 1. CREAR ROBOTS ===")

id1 = manager.add_robot("robot_001")
print(f"Robot creado con ID: {id1}")

id2 = manager.add_robot("robot_002")
print(f"Robot creado con ID: {id2}")

id3 = manager.add_robot("robot_003")
print(f"Robot creado con ID: {id3}")

# ========== 2. LEER TODOS (READ) ==========
print("\n=== 2. LEER TODOS LOS ROBOTS ===")

todos = manager.get_all()
print(f"Total de robots: {len(todos)}")

for robot in todos:
    print(f"  ID: {robot['id']}, Nombre: {robot['robot_id']}")

# ========== 3. BUSCAR UNO (READ) ==========
print("\n=== 3. BUSCAR UN ROBOT ===")

robot = manager.get_robot("robot_002")
if robot:
    print(f"Encontrado: {robot}")
else:
    print("Robot no encontrado")

# ========== 4. ACTUALIZAR (UPDATE) ==========
print("\n=== 4. ACTUALIZAR UN ROBOT ===")

resultado = manager.update_robot("robot_001")
print(f"¿Se actualizó? {resultado}")

# Verificar que se actualizó
robot = manager.get_robot("robot_001")
print(f"Robot actualizado: {robot}")

# ========== 5. ELIMINAR (DELETE) ==========
print("\n=== 5. ELIMINAR UN ROBOT ===")

resultado = manager.delete_robot("robot_002")
print(f"¿Se eliminó? {resultado}")

# Verificar que se eliminó
print("\nRobots restantes:")
todos = manager.get_all()
for robot in todos:
    print(f"  {robot}")

