#version 330

in vec3 in_vert;
uniform mat4 model;

void main() {
    gl_Position = model * vec4(in_vert, 1.0);
}