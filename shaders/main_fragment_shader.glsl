#version 330

out vec4 fragColor;
uniform vec3 color;
uniform float alphaValue = 1.0;

void main() {
    fragColor = vec4(color, alphaValue);
}