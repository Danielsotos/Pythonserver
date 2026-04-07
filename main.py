from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse  
import uvicorn
import json
from datetime import datetime 

app = FastAPI(
    title="Servidor web con FastAPI",
    description="Servidor con frontend + API",
    version="1.0.0",
)

# -------------------------
# STATIC (CSS, JS)
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static") # Monta la carpeta "static" para servir archivos CSS y JS
app.mount("/pictures", StaticFiles(directory="pictures"), name="pictures") # Monta la carpeta "pictures" para servir imágenes


# -------------------------
# HTML
# -------------------------
@app.get("/")
def root():
    return FileResponse("templates/index.html")


@app.get("/FLR")
def flr():
    return FileResponse("templates/FLR.html")


@app.get("/SBS")
def sbs():
    return FileResponse("templates/SBS.html")

@app.get("/datos")
def datos():
    try:
        with open('data/datos.json', 'r') as f:
            datos = json.load(f)
        return JSONResponse(content=datos)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/FLR")
async def guardar_flr(request: Request):
    try:
        data = await request.json()
        id_nuevo = data.get('id')
        
        with open('data/datos.json', 'r') as f:
            datos = json.load(f)
        
        nuevo_robot = {
            'id': id_nuevo,
            'timestamp': datetime.now().isoformat()
        }
        datos['robotsFLR'].append(nuevo_robot)
        
        with open('data/datos.json', 'w') as f:
            json.dump(datos, f, indent=2)
        
        return {"message": "Datos guardados correctamente", "id": id_nuevo}
    except Exception as e:
        return {"error": str(e)}

@app.post("/SBS")
async def guardar_sbs(request: Request):
    try:
        data = await request.json()
        id_nuevo = data.get('id')
        
        with open('data/datos.json', 'r') as f:
            datos = json.load(f)
        
        nuevo_robot = {
            'id': id_nuevo,
            'timestamp': datetime.now().isoformat()
        }
        datos['robotsSBS'].append(nuevo_robot)
        
        with open('data/datos.json', 'w') as f:
            json.dump(datos, f, indent=2)
        
        return {"message": "Datos guardados correctamente", "id": id_nuevo}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080) # Cambia el puerto a 8080
