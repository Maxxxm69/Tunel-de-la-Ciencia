import glfw
import moderngl
import math
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
        return

    glfw.make_context_current(window)
    glfw.swap_interval(0)

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
    out vec3 color_pantalla;
    uniform vec3 lampara_1;
    uniform sampler2D textura;
    uniform vec3 posicion_camara;
    uniform float emisivo;
    uniform float tiempo;
    uniform float fase;
    in vec3 normal_vertice;
    in vec3 posicion_vertice;
    in vec2 out_uvs;

    void main() {
        float seno1 = sin(2.0 * 3.14159265 * 1 *tiempo + fase);
        float seno2 = sin(2.0 * 3.14159265 * 2.7 *tiempo + 2*fase);
        float mezcla = 0.5*(0.7 * seno1 + 0.3 * seno2)+0.5;
        float parpadeo = mix(0.7,mezcla,1.0);

        vec3 dir_cam = normalize(posicion_camara - posicion_vertice);
        vec3 norm = normalize(normal_vertice);
        float distancia = length(posicion_camara - posicion_vertice);
        vec3 v1 = lampara_1 - posicion_vertice;
        float d1 = max(dot(norm, normalize(v1)), 0.0) / (1.0 + 0.095 * dot(v1, v1));
        d1 = d1 * parpadeo;
        float factor = smoothstep(2,20, distancia);
        vec3 total = vec3(d1) + vec3(0.22, 0.10, 0.40);
        
        vec3 v1_norm = normalize(v1);
        vec3 vect_ref = reflect(-dir_cam,norm);
        float cos_especular = max(dot(vect_ref,v1_norm),0.0);
        float potencia = pow(cos_especular,32.0)*d1;

        vec3 colorImage = texture(textura, out_uvs).rgb;
        float luminicencia = smoothstep(0.4,0.6,dot(vec3(0.2126,0.7152,0.0722), colorImage));
        vec3 producto = luminicencia * emisivo * vec3(0.875,1.0,0.0);
        vec3 text_iluminada = colorImage * total + potencia;
        vec3 brillo = text_iluminada + producto;

        color_pantalla = mix(brillo, vec3(0.03, 0.02, 0.07), factor);   
    }
    """

    contx = moderngl.create_context()
    print(f"Debugg GPU detectada : {contx.info['GL_RENDERER']}") 
    contx.enable(moderngl.DEPTH_TEST)
    programa = contx.program(vertex_shader=codigo_vertex, fragment_shader=codigo_fragment)
    a1, a2, uv,cilindro,Objetos,final = modelo.leerArchivo()
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

    lista = []
    for i in range(config.TUNELES):
        lista.append(i)
        lista.append(-i)
        lista = list(set(lista))
    lista.sort()
    limite_z_inferior = (min(lista) * largo - largo / 2)+2
    limite_z_superior = (max(lista) * largo + largo / 2)-2

    glfw.set_cursor_pos_callback(window, camara.mouseCallback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    frames = 0
    #Bucle de renderizado
    inicio = time.perf_counter()
    anterior = time.perf_counter()
    while not glfw.window_should_close(window):
        frames +=1
        ahora = time.perf_counter()
        dt = min(ahora-anterior,0.05)
        anterior = ahora
        if ahora-inicio> 0.5:
            fps = frames/(ahora-inicio)
            glfw.set_window_title(window,f"Tunel de la Ciencia | FPS : {fps:.1f} ")
            inicio = ahora
            frames=0

        glfw.poll_events() 
        matrizPerspectiva = glm.perspective(config.FOV, config.RATIO,0.1,1000)    
        #vectores para la camara
        v1 = glm.vec3(0,1,0)
        v3 = glm.vec3(0,1,-5)
        #vector de movimiento
        vec_mov = glm.vec3(0,0,0)

        camara.direccion_piso = glm.vec3(camara.direccion.x, 0.0, camara.direccion.z)
        camara.direccion_piso = glm.normalize(camara.direccion_piso)
        
        #Movimientos del personaje
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            vec_mov += camara.velocidad * camara.direccion_piso * dt

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            vec_mov -= camara.velocidad * camara.direccion_piso * dt

        derecha = glm.normalize(glm.cross(camara.direccion, v1))

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            vec_mov -= camara.velocidad * derecha * dt
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            vec_mov += camara.velocidad * derecha * dt
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        camara.velo_y -= camara.grav *dt
        camara.v2.y += camara.velo_y *dt

        if camara.v2.y < 1 :
            camara.velo_y = 0
            camara.v2 = glm.vec3(camara.v2.x,1.0,camara.v2.z)
            suelo = True
        else:
            suelo =  False

        if suelo and glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            camara.velo_y = 3.6
        
        #Verificacion si el movimiento cumple con las limitaciones del cilindro
        posicion_candidata =  camara.v2 + vec_mov
        distancia = math.sqrt((centro[0] - posicion_candidata.x)**2 + (centro[1] - posicion_candidata.y)**2)
        posicion_candidata.z = max(limite_z_inferior, min(posicion_candidata.z,limite_z_superior))

        if distancia < radio:
            camara.v2 = posicion_candidata
        else:
            camara.v2 = glm.vec3(camara.v2.x, camara.v2.y, posicion_candidata.z)
        

        matrizCamara = glm.lookAt(camara.v2,camara.v2+camara.direccion,v1)
        programa['matriz_vista'].write(matrizCamara.to_bytes())
        programa['matriz_proyeccion'].write(matrizPerspectiva.to_bytes())
        programa['posicion_camara']=camara.v2
        programa['tiempo'].value=glfw.get_time()

        contx.clear(0.03, 0.02, 0.07, 1.0, depth=1.0)


        #Generacion de las diferentes copias del cilindro
        for i in lista:
            desplazamiento = i*largo
            matriz_traslacion = glm.translate(glm.vec3(0,0,float(desplazamiento)))
            if i%2 == 0:
                matriz_escalar = glm.scale(glm.vec3(1,1,1))
            elif i%2 == 1:
                matriz_escalar = glm.scale(glm.vec3(1,1,-1))
            matriz_modelo = matriz_traslacion * matriz_escalar
            programa['lampara_1'].value = (centro[0], centro[1], centro[2] + desplazamiento)
            programa['matriz_traslacion'].write(matriz_modelo)
            programa['fase'].value= i*1.7
            #Condicional para decidir cual copia le corresponde a la entrada o salida del tunel
            if np.abs(i) >= max(lista):
                programa['emisivo'].value = 0.0
                vao.render(vertices=rangos.get("Cylinder.001").get("cantidad"),first=rangos.get("Cylinder.001").get("inicio"))
            else:
                programa['emisivo'].value = 1.0
                vao.render(vertices=rangos.get("Cylinder").get("cantidad"),first=rangos.get("Cylinder").get("inicio"))
            programa['emisivo'].value = 0.0
            vao.render(vertices=rangos.get("Plane").get("cantidad"),first=rangos.get("Plane").get("inicio"))

        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()