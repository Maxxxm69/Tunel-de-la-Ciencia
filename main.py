import glfw
import moderngl
import math
import glm
import numpy as np
from PIL import Image


ANCHO = int(1920/2)
ALTO = int(1080/2)
FOV = glm.radians(45) 
RATIO = ANCHO/ALTO
SENS = 0.1
IMAGEN = "atlas.png"
yaw = -90.0
pitch = 0.0
last_x = ANCHO / 2
last_y = ALTO / 2
primerMouse = True
direccion = glm.vec3(0.0, 0.0, -1.0)
v2 = glm.vec3(0,1.5,0)
velocidad=0.5
velo_y = 0.0
grav = 0.002

def abrirAtlas():
    with Image.open(IMAGEN) as im:
        canales = im.transpose(method=Image.FLIP_TOP_BOTTOM)
        canales = canales.convert("RGB")
        tamano = canales.size
        px = canales.tobytes()
    return tamano, canales, px



def leerArchivo():
    posiciones, normales = [], []
    out_pos, out_nor = [], []
    vt, out_vt = [], []
    cilindro = []
    objeto = ""
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
    return np.array(out_pos, dtype='f4'), np.array(out_nor, dtype='f4'), np.array(out_vt, dtype='f4'), np.array(cilindro, dtype='f4')

def mouseCallback(window,xpos,ypos):
    global yaw,pitch,last_x,last_y,primerMouse,direccion
    #para evitar el primer sobresalto de la camara
    if(primerMouse):
        last_x = ANCHO/2
        last_y = ALTO/2
        primerMouse = False

    xOff = xpos-last_x
    yOff = last_y-ypos
    last_x = xpos
    last_y = ypos
    xOff *= SENS
    yOff *= SENS
    pitch += yOff
    yaw += xOff
    # restricciones para que no haga movimientos locos
    if(pitch > 89):
        pitch = 89
    if(pitch < -89):
        pitch = -89
    
    direccion_x = math.cos(glm.radians(pitch)) * math.cos(glm.radians(yaw))
    direccion_y = math.sin(glm.radians(pitch)) 
    direccion_z = math.cos(glm.radians(pitch)) * math.sin(glm.radians(yaw))
    direccion = glm.vec3(direccion_x, direccion_y, direccion_z)



def main():
    global v2, velo_y
    #Preparacion del entorno
    #iniciaizacion de glfw
    if not glfw.init():
        #manejo de errores
        raise Exception("No se inicializo glfw")

    #hints los parametros son constantes de GLFW
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    #creacion de una ventana y contexto
    window = glfw.create_window(ANCHO,ALTO, "Tunel de la Ciencia", None, None)
    if not window:
        glfw.terminate()
        raise Exception("No se creo la ventana de GLFW")
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # Bloque 3 Configuracion de 
    codigo_vertex = """
    #version 330 core

    in vec3 in_posicion;
    uniform mat4 matriz_vista;
    uniform mat4 matriz_proyeccion;
    in vec3 in_normales;
    in vec2 in_uvs;
    uniform mat4 matriz_traslacion;

    out vec3 normal_vertice;
    out vec3 posicion_vertice;
    out vec2 out_uvs;

    void main() {
        vec4 vertice_trasladado = matriz_traslacion* vec4(in_posicion, 1.0);
        gl_Position = matriz_proyeccion * matriz_vista * vertice_trasladado;
        normal_vertice = in_normales;
        posicion_vertice = vertice_trasladado.xyz;
        out_uvs = in_uvs;
    }
    """
    codigo_fragment = """
    #version 330 core
    out vec4 color_pantalla;
    uniform vec3 lampara_1;
    uniform vec3 lampara_2;
    uniform sampler2D textura;
    uniform vec3 posicion_camara;

    in vec3 normal_vertice;
    in vec3 posicion_vertice;
    in vec2 out_uvs;

    void main() {
        vec3 norm = normalize(normal_vertice);

        float distancia = length(posicion_camara - posicion_vertice);

        vec3 v1 = lampara_1 - posicion_vertice;
        //vec3 v2 = lampara_2 - posicion_vertice;

        float d1 = max(dot(norm, normalize(v1)), 0.0) / (1.0 + 0.095 * dot(v1, v1));
        //float d2 = max(dot(norm, normalize(v2)), 0.0) / (1.0 + 0.05 * dot(v2, v2));

        float factor = smoothstep(2,20, distancia);
        
        float total = d1 + 0.3;
        
        vec4 colorImage = texture(textura, out_uvs);

        color_pantalla = mix(colorImage * total, vec4(0,0,0,1), factor);
    }
    """

    contx = moderngl.create_context()
    print(f"Debugg GPU detectada : {contx.info['GL_RENDERER']}") 
    contx.enable(moderngl.DEPTH_TEST)
    programa = contx.program(vertex_shader=codigo_vertex, fragment_shader=codigo_fragment)
    a1, a2, uv,cilindro = leerArchivo()
    vbo = contx.buffer(a1.tobytes())
    vbo_normales = contx.buffer(a2.tobytes())
    uv_buffer = contx.buffer(uv.tobytes())
    tamano,canales,px = abrirAtlas()
    textura = contx.texture(tamano,3,px)
    minimapa = textura.build_mipmaps()
    textura.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    textura.use(location=0)
    textura.repeat_y = False
    textura.repeat_x = False
    programa['textura'].value = 0
    minimos = cilindro.min(axis=0)
    maximos = cilindro.max(axis=0)
    centro  = (minimos + maximos) / 2
    radio = np.abs(centro[0] - maximos[0])
    largo = maximos[2] - minimos[2]
    vao = contx.vertex_array(programa, [
        (vbo, '3f', 'in_posicion'),
        (vbo_normales, '3f', 'in_normales'),
        (uv_buffer, '2f', 'in_uvs'),
    ])


    glfw.set_cursor_pos_callback(window, mouseCallback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    #Bucle de renderizado
    while not glfw.window_should_close(window):
        # aca va la renderizacion que hare con ModernGL
        glfw.poll_events() #para procesar los eventos
        matrizPerspectiva = glm.perspective(FOV, RATIO,0.1,1000)    
        #vectores para la camara
        v1 = glm.vec3(0,1,0)
        v3 = glm.vec3(0,1,-5)
        direccion_piso = glm.vec3(direccion.x, 0.0, direccion.z)
        direccion_piso = glm.normalize(direccion_piso)


        vec_mov = glm.vec3(0,0,0)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            vec_mov += velocidad * direccion_piso

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            vec_mov -= velocidad * direccion_piso    

        derecha = glm.normalize(glm.cross(direccion, v1))

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            vec_mov -= velocidad * derecha
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            vec_mov += velocidad * derecha

        velo_y -= grav
        v2.y += velo_y

        if v2.y < 1 :
            velo_y = 0
            v2 = glm.vec3(v2.x,1.0,v2.z)
            suelo = True
        else:
            suelo =  False

        if suelo and glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            velo_y = 0.06
        
        posicion_candidata =  v2 + vec_mov
        distancia = math.sqrt((centro[0] - posicion_candidata.x)**2 + (centro[1] - posicion_candidata.y)**2)
        if distancia < radio:
            v2 = posicion_candidata
        else:
            v2 = glm.vec3(v2.x, v2.y, posicion_candidata.z)

        matrizCamara = glm.lookAt(v2,v2+direccion,v1)
        programa['matriz_vista'].write(matrizCamara.to_bytes())
        programa['matriz_proyeccion'].write(matrizPerspectiva.to_bytes())
        #al final se debe limpiar la pantalla para mostrar lo siguiente 
        contx.clear(0.15,0.15,0.15, 1.0, depth=1.0)

        for i in (-1,0,1):
            desplazamiento = i*largo
            matriz_modelo = glm.translate(glm.vec3(0,0,float(desplazamiento)))
            programa['matriz_traslacion'].write(matriz_modelo.to_bytes())
            programa['lampara_1'].value = (centro[0], centro[1], centro[2] + desplazamiento)
            vao.render()
        programa['posicion_camara']=v2
        #como glfw usa dos buffers uno para mostrar y otro para procesar
        #de fondo hay que indicar que haga el swap de estos buffers
        glfw.swap_buffers(window)
    
    # terminar y cerrar glfw
    glfw.terminate()

if __name__ == "__main__":
    main()