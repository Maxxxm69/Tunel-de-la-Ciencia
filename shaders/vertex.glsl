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