import glm
from pathlib import Path

carpeta = Path(__file__).parent
fragment_ruta = carpeta / "shaders" / "fragment.glsl"
vertex_ruta = carpeta / "shaders" / "vertex.glsl"

SENS = 0.1
TUNELES=6
ANCHO = int(1920/2)
ALTO = int(1080/2)
FOV = glm.radians(45) 
RATIO = ANCHO/ALTO
IMAGEN = "atlas.png"
SALTO=3.6
LIMITE_DT=0.05
FASE=1.7
PLANO_1=0.1
PLANO_2=1000
INTER_FPS=0.5
SUELO=1