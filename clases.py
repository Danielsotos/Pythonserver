from datetime import datetime
from pathlib import Path
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PASO 1: Crear la base para los modelos
Base = declarative_base()


# PASO 2: Definir el modelo de la tabla
class RobotRegistro(Base):
    __tablename__ = "robots"
    
    id = Column(Integer, primary_key=True)
    section = Column(String)  # Sección: "robotsFLR" o "robotsSBS"
    robot_id = Column(String)  # ID del robot
    timestamp = Column(DateTime)  # Fecha y hora


# PASO 3: Gestor de la base de datos
class RobotDataManager:
    def __init__(self, db_path="data/robots.db"):
        # Crear carpeta si no existe
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # PASO 4: Conectar con la base de datos
        self.engine = create_engine(f"sqlite:///{db_path}")
        
        # PASO 5: Crear las tablas
        Base.metadata.create_all(self.engine)
        
        # PASO 6: Crear el generador de sesiones
        self.Session = sessionmaker(bind=self.engine)
    
    # ========== CREAR UN ROBOT ==========
    def add_robot(self, section, robot_id):
        """Añade un nuevo robot a la base de datos"""
        
        session = self.Session()
        
        # Crear un nuevo registro
        nuevo_robot = RobotRegistro(
            section=section,
            robot_id=robot_id,
            timestamp=datetime.now()
        )
        
        # Guardar
        session.add(nuevo_robot)
        session.commit()
        session.close()
        
        return nuevo_robot.id
    
    # ========== OBTENER TODOS LOS ROBOTS ==========
    def get_all(self):
        """Obtiene todos los robots organizados por sección"""
        
        session = self.Session()
        
        # Buscar todos los robots
        robots = session.query(RobotRegistro).all()
        
        # Organizar por sección
        datos = {}
        for robot in robots:
            # Si la sección no existe, crearla
            if robot.section not in datos:
                datos[robot.section] = []
            
            # Añadir el robot a su sección
            datos[robot.section].append({
                "id": robot.robot_id,
                "timestamp": str(robot.timestamp)
            })
        
        session.close()
        
        return datos
    
    # ========== BUSCAR UN ROBOT ==========
    def get_robot(self, robot_id):
        """Busca un robot por su ID"""
        
        session = self.Session()
        
        robot = session.query(RobotRegistro).filter_by(robot_id=robot_id).first()
        
        session.close()
        
        if robot:
            return {
                "id": robot.robot_id,
                "section": robot.section,
                "timestamp": str(robot.timestamp)
            }
        else:
            return None
    
    # ========== ACTUALIZAR UN ROBOT ==========
    def update_robot(self, robot_id):
        """Actualiza el timestamp de un robot"""
        
        session = self.Session()
        
        robot = session.query(RobotRegistro).filter_by(robot_id=robot_id).first()
        
        if robot:
            robot.timestamp = datetime.now()
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    
    # ========== ELIMINAR UN ROBOT ==========
    def delete_robot(self, robot_id):
        """Elimina un robot"""
        
        session = self.Session()
        
        robot = session.query(RobotRegistro).filter_by(robot_id=robot_id).first()
        
        if robot:
            session.delete(robot)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
