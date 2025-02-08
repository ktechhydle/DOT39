def hexToRGB(hex_code) -> tuple[float, float, float]:
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


def isConvertibleToFloat(value):
    try:
        return float(value)
    except ValueError:
        return None


vertex_shad = open('shaders/main_vertex_shader.glsl', 'r').read()
fragment_shad = open('shaders/main_fragment_shader.glsl', 'r').read()

