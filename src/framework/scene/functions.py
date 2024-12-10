def hexToRGB(hex_code):
    """
    Converts a hex color code to an RGB tuple.

    Parameters:
        hex_code (str): Hex color code in the format "#RRGGBB" or "RRGGBB".

    Returns:
        tuple: A tuple representing the RGB color (red, green, blue).
    """
    # Remove the '#' if it's included in the hex code
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return r, g, b


vertex_shad = '''
#version 330 core

in vec2 in_position; // Vertex position attribute
in vec3 in_color;    // Vertex color attribute

out vec3 frag_color; // Pass color to fragment shader

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0); // Transform to clip space
    frag_color = in_color; // Pass color to the fragment shader
}
'''

fragment_shad = '''
#version 330 core

in vec3 frag_color; // Interpolated color from vertex shader

out vec4 out_color; // Final output color

void main() {
    out_color = vec4(frag_color, 1.0); // Output color with full opacity
}
'''

