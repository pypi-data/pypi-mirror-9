""" Primitive geodetic operations on planes and spheres """

import math

def _plane_azimuth(dx, dy):
    """ Calculate azimuth given an offset *dx* and *dy* for scalar input """
    if dx > 0:
        if dy > 0:
            return math.atan(dx/dy)
        elif dy < 0:
            return math.pi - math.atan(-dx/dy)
        else:
            return 0.5*math.pi
    elif dx < 0:
        if dy > 0:
            return 2*math.pi - math.atan(-dx/dy)
        elif dy < 0:
            return math.pi + math.atan(dx/dy)
        else:
            return 1.5*math.pi
    else:
        if dy > 0:
            return 0.0
        else:
            return math.pi

def plane_azimuth(dx, dy):
    if hasattr(dx, "__iter__"):
        return numpy.array([_plane_azimuth(dx_, dy_) for dx_, dy_ in zip(dx, dy)])
    else:
        return _plane_azimuth(dx, dy)


