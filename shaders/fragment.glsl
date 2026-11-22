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