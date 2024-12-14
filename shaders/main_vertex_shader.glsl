#version 330

in vec3 in_vert;
uniform mat4 matrix; // Camera matrix

void main() {
    vec4 transformed = matrix * vec4(in_vert, 1.0);

    gl_Position = transformed;
}
