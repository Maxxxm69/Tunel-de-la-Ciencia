import config
import glm

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
    #para evitar el primer sobresconfig.ALTO de la camara
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

