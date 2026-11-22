import numpy as np

def leerArchivo():
    posiciones, normales = [], []
    out_pos, out_nor = [], []
    vt, out_vt = [], []
    cilindro = []
    objeto = ""
    Objetos={}
    with open("cilindro.obj") as f:
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
