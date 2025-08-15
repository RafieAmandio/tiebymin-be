import math

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = [x / 255.0 for x in rgb]

    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    x /= 0.95047
    y /= 1.00000
    z /= 1.08883

    x = x ** (1/3) if x > 0.008856 else (7.787 * x) + (16 / 116)
    y = y ** (1/3) if y > 0.008856 else (7.787 * y) + (16 / 116)
    z = z ** (1/3) if z > 0.008856 else (7.787 * z) + (16 / 116)

    L = (116 * y) - 16
    a = 500 * (x - y)
    b_ = 200 * (y - z)
    
    return L, a, b_

def calculate_delta_e(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    return math.sqrt((L2 - L1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2)