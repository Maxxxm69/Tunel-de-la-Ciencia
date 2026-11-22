import config
import glm
import glfw
import math
import modelo

yaw = -90.0
pitch = 0.0
last_x = config.ANCHO / 2
last_y = config.ALTO / 2
primerMouse = True
direccion = glm.vec3(0.0, 0.0, -1.0)
v2 = glm.vec3(0,1.5,0)
velocidad=3.0
velo_y = 0.0
grav = 7.2

def mouseCallback(window,xpos,ypos):
    global yaw,pitch,last_x,last_y,primerMouse,direccion
    #para evitar el primer sobresalto de la camara
    if(primerMouse):
        last_x = config.ANCHO/2
        last_y = config.ALTO/2
        primerMouse = False

    xOff = xpos-last_x
    yOff = last_y-ypos
    last_x = xpos
    last_y = ypos
    xOff *= config.SENS
    yOff *= config.SENS
    pitch += yOff
    yaw += xOff
    #restricciones en la camara para evitar movimientos indeseados
    if(pitch > 89):
        pitch = 89
    if(pitch < -89):
        pitch = -89
    
    direccion_x = math.cos(glm.radians(pitch)) * math.cos(glm.radians(yaw))
    direccion_y = math.sin(glm.radians(pitch)) 
    direccion_z = math.cos(glm.radians(pitch)) * math.sin(glm.radians(yaw))
    direccion = glm.vec3(direccion_x, direccion_y, direccion_z)

#vectores para la camara
v1 = glm.vec3(0,1,0)
 #vector de movimiento


#Movimientos del personaje
def movimientoPersonaje(window,dt):
    global velo_y,grav,v2,v1
    vec_mov = glm.vec3(0,0,0)
    direccion_piso = glm.vec3(direccion.x, 0.0,direccion.z)
    direccion_piso = glm.normalize(direccion_piso)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        vec_mov += velocidad * direccion_piso * dt
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        vec_mov -= velocidad * direccion_piso * dt
    derecha = glm.normalize(glm.cross( direccion, v1))
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        vec_mov -= velocidad * derecha * dt
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        vec_mov += velocidad * derecha * dt
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    velo_y -= grav *dt
    v2.y += velo_y *dt
    if v2.y < config.SUELO:
        velo_y = 0
        v2 = glm.vec3( v2.x,config.SUELO, v2.z)
        suelo = True
    else:
        suelo =  False
    if suelo and glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        velo_y = config.SALTO

    #Verificacion si el movimiento cumple con las limitaciones del cilindro
    posicion_candidata =  v2 + vec_mov
    distancia = math.sqrt((modelo.centro[0] - posicion_candidata.x)**2 + (modelo.centro[1] - posicion_candidata.y)**2)
    posicion_candidata.z = max(modelo.limite_z_inferior, min(posicion_candidata.z,modelo.limite_z_superior))
    if distancia < modelo.radio:
        v2 = posicion_candidata
    else:
        v2 = glm.vec3( v2.x, v2.y, posicion_candidata.z)
            
