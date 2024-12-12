#version 330

in vec3 in_vert;
uniform vec3 position; // Item rendered position
uniform mat4 matrix; // Camera matrix

void main() {
    vec4 transformed = matrix * vec4(in_vert + position, 1.0);

    gl_Position = transformed;
}
