import pygame
import math


def box_shadow(size: list, color: pygame.Color, radius: int):
    vec_size = pygame.Vector2(size)
    gcd = math.gcd(*size)

    surface = pygame.Surface(vec_size // 12, pygame.SRCALPHA)
    offset = 1
    pygame.draw.rect(
        surface,
        color,
        [
            offset,
            offset,
            surface.get_width() - offset * 2,
            surface.get_height() - offset * 2,
        ],
        0,
        1,
    )
    surface = pygame.transform.smoothscale(
        surface, [size[0] + radius, size[1] + radius]
    )
    surface.set_alpha(170)
    return surface
