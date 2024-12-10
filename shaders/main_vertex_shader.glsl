#version 330

in vec3 in_vert;
uniform mat4 model;
uniform float aspectRatio;

void main() {
    vec4 transformed = model * vec4(in_vert, 1.0);
    // Apply the aspect ratio correction
    transformed.x /= aspectRatio;
    gl_Position = transformed;
}
