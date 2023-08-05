__author__ = 'chick'

import cv2
import numpy

def f(h, v):
    """
    compute an rgb value for hue and value, here saturation is set to max (255)
    :param h: hue, must be in degrees
    :param v: value, must be 0 <= v < 1.0
    :return: red, green, blue
    """
    """
    Expects all HSV values in [0, 1], and returns RGB values in [0, 1].
    """
    s = 1
    c = v * s
    x = c * (1 - abs(h/60.0 % 2 - 1))
    m = v - c
    if h < 60: r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    elif h < 360: r, g, b = c, 0, x
    return (r+m)*255, (g+m)*255, (b+m)*255


def f2(h, v):
    """Convert HSV color space to RGB color space

    @param h: Hue
    @param s: Saturation
    @param v: Value
    return (r, g, b)
    """
    s = 1
    import math
    hi = math.floor(h / 60.0) % 6
    f =  (h / 60.0) - math.floor(h / 60.0)
    p = v * (1.0 - s)
    q = v * (1.0 - (f*s))
    t = v * (1.0 - ((1.0 - f) * s))
    return {
        0: (v, t, p),
        1: (q, v, p),
        2: (p, v, t),
        3: (p, q, v),
        4: (t, p, v),
        5: (v, p, q),
    }[hi]

def g(h, v):
    print("hue {} value {} -> {}".format(h, v, f(h, v)))


g(270, .5)
g(0, .5)
g(90, .5)
g(180, .5)
