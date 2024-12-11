#version 330

in vec3 in_vert;
uniform mat4 model;
uniform vec3 position;

uniform float aspectRatio;
uniform vec3 cameraPosition;
uniform float cameraZoom;
uniform float cameraYaw;
uniform float cameraPitch;

void main() {
    vec4 transformed = model * vec4(in_vert, 1.0);

    // Apply the aspect ratio correction
    transformed.x /= aspectRatio;

    // Add item position offset
    transformed.xyz += position;
    gl_Position = transformed;
}
