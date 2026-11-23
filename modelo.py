import numpy as np
import config

def leerArchivo():
    posiciones, normales = [], []
    out_pos, out_nor = [], []
    vt, out_vt = [], []
    cilindro = []
    objeto = ""
    Objetos={}
    with open("recursos/cilindro.obj") as f:
        for linea in f:
            if linea.startswith("v "):
                posiciones.append([float(a) for a in linea.split()[1:]])
            elif linea.startswith("vn "):
                normales.append([float(a) for a in linea.split()[1:]])
            elif linea.startswith("vt "):
                vt.append([float(a) for a in linea.split()[1:]])
            elif linea.startswith("f "):
                cara = [p.split("/") for p in linea.split()[1:]]
                for i in range(1, len(cara) - 1):
                    for k in (0, i, i + 1):
                        v = cara[k]
                        out_pos.append(posiciones[int(v[0]) - 1])
                        if objeto == "Cylinder":
                            cilindro.append(posiciones[int(v[0]) - 1])
                        out_vt.append(vt[int(v[1]) - 1])
                        out_nor.append(normales[int(v[2]) - 1])
            elif linea.startswith("o "):
                objeto = linea.split()[1:][0]
                Objetos[objeto] = len(out_pos)
            if linea.startswith(""):
                ultima = len(out_pos)
    return np.array(out_pos, dtype='f4'), np.array(out_nor, dtype='f4'), np.array(out_vt, dtype='f4'),np.array(cilindro, dtype='f4'),Objetos,ultima


posiciones,normales, uv,cilindro,Objetos,final = leerArchivo()
claves = list(Objetos.keys())
rangos = {}
for i, nombre in enumerate(claves):
    inicio = Objetos[nombre]
    if i+1< len(claves):
        siguiente_inicio = Objetos[claves[i + 1]]
        cantidad = siguiente_inicio - inicio
    else:
        cantidad = final - inicio
    
    rangos[nombre]={
        'inicio':inicio,
        'cantidad':cantidad,
    }
minimos = cilindro.min(axis=0)
maximos = cilindro.max(axis=0)
centro  = (minimos + maximos) / 2
radio = np.abs(centro[0] - maximos[0])
largo = maximos[2] - minimos[2]

lista = []
for i in range(config.TUNELES):
    lista.append(i)
    lista.append(-i)
    lista = list(set(lista))
lista.sort()
limite_z_inferior = (min(lista) * largo - largo / 2)+2
limite_z_superior = (max(lista) * largo + largo / 2)-2
