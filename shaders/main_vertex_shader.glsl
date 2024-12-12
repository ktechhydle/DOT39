#version 330

in vec3 in_vert;
uniform vec3 position; // Item rendered position
uniform mat4 matrix; // Camera matrix

uniform float aspectRatio;
uniform float cameraZoom = 1.0;

void main() {
    vec4 transformed = matrix * vec4((in_vert + position) * cameraZoom, 1.0);

    transformed.x /= aspectRatio;

    gl_Position = transformed;
}
