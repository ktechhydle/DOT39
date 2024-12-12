#version 330

in vec3 in_vert;
uniform vec3 position; // Item rendered position

uniform float aspectRatio;
uniform vec3 cameraPosition;
uniform float cameraZoom = 1.0;

void main() {
    vec4 transformed = vec4((in_vert + position) * cameraZoom, 1.0);

    // Apply the aspect ratio correction
    transformed.x /= aspectRatio;

    gl_Position = transformed;
}
