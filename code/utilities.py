import pygame

# Scale a surface by a given scale factor
def scale_surface(surf, scale_factor):
    scaled_size = pygame.Vector2(surf.get_size()) * scale_factor
    return pygame.transform.scale(surf, scaled_size)

# Scale a surface and optionally flip it horizontally or vertically
def scale_and_flip_surface(surf, scale_factor, flip_x = False, flip_y = False):
    scaled = scale_surface(surf, scale_factor)
    
    if flip_x or flip_y:
        scaled = pygame.transform.flip(scaled, flip_x, flip_y)
    return scaled 
