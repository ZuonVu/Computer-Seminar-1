import pygame
from settings import *
from random import choice, randint
from math import sin, cos
from pygame.math import Vector2
from utilities import * 

class Scrolling_Sprites(pygame.sprite.Sprite):
    def __init__(self, groups, image_path, scale_factor, scroll_speed):
        super().__init__(groups)
        
        # Load and scale the image
        surf = pygame.image.load(image_path).convert_alpha()
        self.image_1 = scale_surface(surf, scale_factor)
        
        # Get the width of the first image
        self.bg_width = self.image_1.get_width()
        
        # Create another image which is similar with the first
        self.image_2 = self.image_1.copy()

        # Set the image and rect for the first image
        self.image = self.image_1  
        self.rect = self.image.get_rect(topleft=(0, 0))  # Define the position of the image
        
        # Positioning
        self.x1 = 0
        self.x2 = self.bg_width
        
        # Scrolling speed
        self.scroll_speed = scroll_speed
        
    def update(self, dt):
        # Move the images horizontally by the scroll speed
        self.x1 -= self.scroll_speed * 0.8 * dt
        self.x2 -= self.scroll_speed * 0.8 * dt
        
        # If one image moves off the screen, reset it to the right of the other image
        if self.x1 <= -self.bg_width:
            self.x1 = self.x2 + self.bg_width

        if self.x2 <= -self.bg_width:
            self.x2 = self.x1 + self.bg_width
        
    def draw_bg(self, surface):
        surface.blit(self.image_1, (self.x1, self.rect.y))
        surface.blit(self.image_2, (self.x2, self.rect.y))        
        
class Background(Scrolling_Sprites): 
    def __init__(self, groups, scale_factor):
        super().__init__(groups, 'Background/background.png', scale_factor, 400)

class Ground(Scrolling_Sprites):
    def __init__(self, groups, scale_factor):
        super().__init__(groups, 'Background/ground.png', scale_factor, 360)
        self.sprite_type = 'ground'

        # Adjust the positioning for the ground (set it to the bottom of the screen)
        self.rect.bottomleft = (0, SCREEN_HEIGHT)
        self.pos = pygame.Vector2(self.rect.topleft)
        
        self.mask_1 = pygame.mask.from_surface(self.image_1)
        self.mask_2 = pygame.mask.from_surface(self.image_2)

class Animal(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, folder, frame_count):
        super().__init__(groups)
        self.scale_factor = scale_factor 
        self.frames = []
        self.frame_index = 0
        self.import_frames(folder, frame_count)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.gravity = 1100
        self.velocity = 0
        self.move_speed = 700
        
        self.enemy_speed = 1
        
    def import_frames(self, folder, frame_count):
        for i in range(frame_count):
            surf = pygame.image.load(f'{folder}/{folder}{i}.png').convert_alpha() 
            scaled = scale_surface(surf, self.scale_factor)
            self.frames.append(scaled)
            
    def animate(self, dt, animate_speed):
        self.frame_index += animate_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def bound_check(self):
        if self.rect.right <= 0:
            self.kill()

class Bird(Animal):
    def __init__(self, groups, scale_factor):
        super().__init__(groups, scale_factor, 'Bird', 3)
        self.sprite_type = 'bird'
        self.rect = self.image.get_rect(midleft = (SCREEN_WIDTH / 8, SCREEN_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.moving_left = False
        self.moving_right = False
        
    def apply_gravity(self, dt):
        self.velocity += self.gravity * dt
        self.pos.y += self.velocity * dt
        self.rect.y = int(self.pos.y)
        
    def jump(self):
        self.velocity = -420
        
    def rotate(self): 
        self.image = pygame.transform.rotozoom(self.frames[int(self.frame_index)], -self.velocity * 0.05, 1)
        
    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt, 10) 
        self.rotate() 
        
        if self.moving_left:
            self.pos.x -= self.move_speed * dt
        if self.moving_right:
            self.pos.x += self.move_speed * dt
            
        self.rect.x = int(self.pos.x)  

class Pig(Animal):
    def __init__(self, groups, scale_factor):
        super().__init__(groups, scale_factor, 'Pigs', 2)
        self.sprite_type = 'pig'
        self.rect = self.image.get_rect(bottomright = (SCREEN_WIDTH + randint(120, 300), randint(150, SCREEN_HEIGHT - 100)))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)
        self.wave_amplitude = randint(300, 750)
        self.speed_random = randint(400, 600)
        
    def update(self, dt):
        self.animate(3, dt)
        self.pos.x -= self.enemy_speed * self.speed_random * dt 
        self.pos.y +=  sin(pygame.time.get_ticks() / 100) * self.wave_amplitude * dt
        
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        self.bound_check()
        
class Enemy_Bird(Animal):
    def __init__(self, groups, scale_factor):
        super().__init__(groups, scale_factor, 'Enemy', 3)
        self.sprite_type = 'enemy' 
        
        # Flip all frames horizontally
        self.frames = [scale_and_flip_surface(frame, 1, flip_x = True) for frame in self.frames]
       
        # After flipping, update image, rect, mask
        self.image = self.frames[self.frame_index]
       
        self.rect = self.image.get_rect(bottomright = (SCREEN_WIDTH + randint(120, 300), randint(150, SCREEN_HEIGHT - 100)))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.wave_amplitude = randint(300, 750)
        self.speed_random = randint(400, 600)
            
    def update(self, dt):
        self.animate(3, dt)
        self.pos.x -= self.enemy_speed * self.speed_random * dt 
        self.pos.y +=  cos(pygame.time.get_ticks() / 100) * self.wave_amplitude * dt 
        
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        self.bound_check()
        
class Logs(pygame.sprite.Sprite): 
    def __init__(self, groups, position, scroll_speed):
        super().__init__(groups)
        
        self.sprite_type = 'log'
        
        self.scroll_speed = scroll_speed
        
        surf = pygame.image.load(f'Logs/Logs{choice((1,4))}.png').convert_alpha() 
              
        top_y = randint(-250, 0)
        bottom_y = SCREEN_HEIGHT + randint(0, 250)
        gap = randint(250, 550)
        x = SCREEN_WIDTH 
              
        # position 1 is from the top, -1 is from the bottom
        
        if position == 1:
            self.image = scale_and_flip_surface(surf, 2.5, flip_y = True)
            self.rect = self.image.get_rect(topleft = (x + randint(20, 300) , top_y - gap // 2))
            self.pos = pygame.Vector2(self.rect.topleft)

        if position == -1:
            self.image = scale_surface(surf, 2.5)
            self.rect = self.image.get_rect(bottomleft = (x + randint(20, 300), bottom_y + gap // 2))
            self.pos = pygame.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= self.scroll_speed * 200 * dt 
        self.rect.x = int(self.pos.x)
        
        if self.rect.right <= 0:
            self.kill()
            

        
        

    
