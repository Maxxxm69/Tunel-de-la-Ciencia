import glfw
import moderngl
import glm
import numpy as np
from PIL import Image
import time
import config
import modelo
import camara

def abrirAtlas():
    with Image.open(config.IMAGEN) as im:
        canales = im.transpose(method=Image.FLIP_TOP_BOTTOM)
        canales = canales.convert("RGB")
        tamano = canales.size
        px = canales.tobytes()
    return tamano, canales, px

def generarTuneles(programa,maximo,vao,vertices_Cylinder,first_Cylinder,vertices_Cylinder1,first_Cylinder1,vertices_Plane,first_Plane):
    #Generacion de las diferentes copias del cilindro
    for i in modelo.lista:
        desplazamiento = i*modelo.largo
        matriz_traslacion = glm.translate(glm.vec3(0,0,float(desplazamiento)))
        if i%2 == 0:
            matriz_escalar = glm.scale(glm.vec3(1,1,1))
        elif i%2 == 1:
            matriz_escalar = glm.scale(glm.vec3(1,1,-1))
        matriz_modelo = matriz_traslacion * matriz_escalar
        programa['lampara_1'].value = (modelo.centro[0], modelo.centro[1], modelo.centro[2] + desplazamiento)
        programa['matriz_traslacion'].write(matriz_modelo)
        programa['fase'].value= i*config.FASE
        #Condicional para decidir cual copia le corresponde a la entrada o salida del tunel
        if np.abs(i) >= maximo:
            programa['emisivo'].value = 0.0
            vao.render(vertices=vertices_Cylinder1,first=first_Cylinder1)
        else:
            programa['emisivo'].value = 1.0
            vao.render(vertices=vertices_Cylinder,first=first_Cylinder)
        programa['emisivo'].value = 0.0
        vao.render(vertices=vertices_Plane,first=first_Plane)

def main():
    #Preparacion del entorno
    #iniciaizacion de glfw
    if not glfw.init():
        #manejo de errores
        raise Exception("No se inicializo glfw")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    #creacion de una ventana y contexto
    window = glfw.create_window(config.ANCHO,config.ALTO, "Tunel de la Ciencia", None, None)
    if not window:
        glfw.terminate()
        raise Exception("No se creo la ventana de GLFW")

    glfw.make_context_current(window)
    glfw.swap_interval(0)

    # Bloque 3 Configuracion de 
    codigo_vertex = config.vertex_ruta.read_text(encoding="utf-8")
    codigo_fragment = config.fragment_ruta.read_text(encoding="utf-8")

    contx = moderngl.create_context()
    print(f"Debugg GPU detectada : {contx.info['GL_RENDERER']}") 
    contx.enable(moderngl.DEPTH_TEST)
    programa = contx.program(vertex_shader=codigo_vertex, fragment_shader=codigo_fragment)

    vbo = contx.buffer(modelo.posiciones.tobytes())
    vbo_normales = contx.buffer(modelo.normales.tobytes())
    uv_buffer = contx.buffer(modelo.uv.tobytes())
    tamano,canales,px = abrirAtlas()
    textura = contx.texture(tamano,3,px)
    textura.build_mipmaps()
    textura.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    textura.use(location=0)
    textura.repeat_y = False
    textura.repeat_x = False
    programa['textura'].value = 0
    
    vao = contx.vertex_array(programa, [
        (vbo, '3f', 'in_posicion'),
        (vbo_normales, '3f', 'in_normales'),
        (uv_buffer, '2f', 'in_uvs'),
    ])
    
    glfw.set_cursor_pos_callback(window, camara.mouseCallback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    frames = 0
    inicio = time.perf_counter()
    anterior = time.perf_counter()
    matrizPerspectiva = glm.perspective(config.FOV, config.RATIO,config.PLANO_1, config.PLANO_2)
    maximo = max(modelo.lista)
    vertices_Cylinder1=modelo.rangos.get("Cylinder.001").get("cantidad")
    first_Cylinder1=modelo.rangos.get("Cylinder.001").get("inicio")
    vertices_Cylinder=modelo.rangos.get("Cylinder").get("cantidad")
    first_Cylinder=modelo.rangos.get("Cylinder").get("inicio")
    vertices_Plane=modelo.rangos.get("Plane").get("cantidad")
    first_Plane=modelo.rangos.get("Plane").get("inicio")

    #Bucle de renderizado
    while not glfw.window_should_close(window):
        frames +=1
        ahora = time.perf_counter()
        dt = min(ahora-anterior,config.LIMITE_DT)
        anterior = ahora
        if ahora-inicio> config.INTER_FPS:
            fps = frames/(ahora-inicio)
            glfw.set_window_title(window,f"Tunel de la Ciencia | FPS : {fps:.1f} ")
            inicio = ahora
            frames=0

        glfw.poll_events()     
        camara.movimientoPersonaje(window,dt)
        
        matrizCamara = glm.lookAt(camara.v2,camara.v2+camara.direccion,camara.v1)
        programa['matriz_vista'].write(matrizCamara.to_bytes())
        programa['matriz_proyeccion'].write(matrizPerspectiva.to_bytes())
        programa['posicion_camara']=camara.v2
        programa['tiempo'].value=glfw.get_time()
        contx.clear(0.03, 0.02, 0.07, 1.0, depth=1.0)

        generarTuneles(programa,maximo,vao,vertices_Cylinder,first_Cylinder,vertices_Cylinder1,first_Cylinder1,vertices_Plane,first_Plane)

        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()