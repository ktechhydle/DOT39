#version 330

in vec3 in_vert;

uniform mat4 matrix; // Camera matrix
uniform vec2 cs_offset;

void main() {
    vec4 transformed = matrix * vec4(in_vert, 1.0);

    transformed.xy += cs_offset;

    gl_Position = transformed;
}
