def rgb_to_hex(rgb):
    if isinstance(rgb, tuple) and len(rgb) == 3:
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    return None

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return None