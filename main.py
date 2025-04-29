import pygame, time
from settings import *
from sprites import *
import random
from random import choice, randint 
from utilities import * 

class AppMain:
    def __init__(self):
        # setup
        pygame.init()
        
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Happy Bird')
        
        self.clock = pygame.time.Clock()
        
        self.flying = False  # Bird not flying yet
        self.paused = False # Game not paused
        
        # create Sprites Group
        
        self.bg_sprites = pygame.sprite.Group()
        self.ground_sprites = pygame.sprite.Group()
        self.collide_sprites = pygame.sprite.Group()
        
        # scale factor
        bg_height = pygame.image.load('Background/background.png').get_height()
        # initialize the scale_factor but this will be adjust for different elements in the game 
        self.scale_factor = SCREEN_HEIGHT / bg_height
        
        # speed

        self.scroll_speed = 1     
        
        # score
        
        try:
            with open('best_score.txt', 'r') as file:
                self.best_score = int(file.read())
        except: 
            self.best_score = 0
        
        self.score = 0
                        
        # sprite setup
        Background(self.bg_sprites, self.scale_factor)
        Ground([self.ground_sprites, self.collide_sprites], self.scale_factor)
        
        # text 
        self.font = pygame.font.Font('Font/BD_Cartoon_Shout.ttf', 35)
        
        # timer
        
        # obstacle timer 
        self.obstacle_timer = pygame.USEREVENT + 1 # new event for obstacles, including logs, pigs, and enemy birds
        self.obstacle_spawn_time = 1100 # spawn time for creating the new obstacle is 1100 ms
        pygame.time.set_timer(self.obstacle_timer, self.obstacle_spawn_time) 

        # flash timer  
        self.flash_text_timer = pygame.USEREVENT + 2  # new event for flashing text
        self.flash_text_active = False  # initially the flash text is inactive
        self.flash_text_duration = 1000  # duration for the New High Score text is 1000 ms
        self.flash_text_surface = self.font.render("New High Score!", True, 'yellow')  # Flash text surface
        self.flash_text_rect = self.flash_text_surface.get_rect(topleft=(20, 100))  
        
        # menu 
        self.menu_surf = pygame.image.load('UI/menu.png').convert_alpha()
        self.menu_surf = scale_surface(self.menu_surf, self.scale_factor * 0.5)
        self.menu_rect = self.menu_surf.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT /2))
    
    # remove method used to delete all elements except the ground and background, then end the game
    def remove(self):
        for sprite in self.collide_sprites:
            if sprite.sprite_type in ['log', 'enemy', 'pig', 'bird']:
                sprite.kill()

        self.flying = False
    
    # Methods handling collisions
    # 1. Collisions with the boundaries:    
    def check_boundary_collision(self):
        if self.bird.rect.top <= 0 or self.bird.rect.left <= 0 or self.bird.rect.right >= SCREEN_WIDTH: 
            self.remove()
            
    # 2. Collisions with dynamic sprites (ground, log, enemy, pig)        
    def check_dynamic_collision(self):
        collisions = pygame.sprite.spritecollide(self.bird, self.collide_sprites, False, pygame.sprite.collide_mask)
        
        for sprite in collisions: 
            if sprite.sprite_type in ['ground', 'log', 'enemy']:
                self.remove()
                return # Stop further checks after a collision is handled
            elif sprite.sprite_type == 'pig':
                sprite.kill()
                self.score += 1
            
    def collisions(self):
        # Check for boundary collisions first
        self.check_boundary_collision()

        # Then check for collisions with obstacles
        self.check_dynamic_collision()
    
    # Method to display score (the number of pigs collided) 
    def display_score(self):
        score_surf = self.font.render(f'Pig: {self.score}', True, 'green')
        score_rect = score_surf.get_rect(topleft=(20, 20))
        self.display_surface.blit(score_surf, score_rect)
        
        best_score_surf = self.font.render(f'High Score: {self.best_score}', True, 'red')
        best_score_rect = best_score_surf.get_rect(topleft=(20, 60))
        self.display_surface.blit(best_score_surf, best_score_rect)
        
        if self.score > self.best_score: 
            self.best_score = self.score 
            try:
                with open('best_score.txt', 'w') as file:
                    file.write(str(self.best_score))
            except:
                pass  # save measurements so that the game wont crash (not very good programming practice but acceptable for this game)
            
            # Activate flash text only if it is not already active
            if not self.flash_text_active:
                self.flash_text_active = True
                pygame.time.set_timer(self.flash_text_timer, self.flash_text_duration)  
                
        # Display the "New high score!" when it is active
        if self.flash_text_active:
            self.display_surface.blit(self.flash_text_surface, self.flash_text_rect)
    
    def draw_text_box(self, surface, rect_color, text, text_color, x, y):
        box_rect = pygame.Rect(x, y, 350, 50) 
        pygame.draw.rect(surface, rect_color, box_rect)
        text_surf = self.font.render(text, True, text_color) 
        text_rect = text_surf.get_rect(center = box_rect.center)
        surface.blit(text_surf, text_rect)
        
    def draw_scrolling_sprites(self, group):
        for sprite in group:
            sprite.draw_bg(self.display_surface) # a method cannot be called on a sprites group -> iterate through each sprite of the groups
            
    # Update and draw all game objects when the game is not paused
    def update_game_objects(self, dt):
        self.display_surface.fill('skyblue') # 1. Clear the screen 
        
        # 2. Update all the sprites
        self.bg_sprites.update(dt) # Update background position
        self.ground_sprites.update(dt) # Update ground position
        self.collide_sprites.update(dt) # Update other things 

        # 3. Draw all the sprites, scores
        
        self.draw_scrolling_sprites(self.bg_sprites) 
        self.draw_scrolling_sprites(self.ground_sprites)
        
        # ground is already handled above so there is no need to draw it again in collide_sprites
        for sprite in self.collide_sprites:
            if sprite.sprite_type != 'ground':
                self.display_surface.blit(sprite.image, sprite.rect)
                
        # Draw score and text
        self.display_score()

        # 4. Check collisions
        self.collisions()
    
    # The main game run method    
    def run(self):
        last_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # calculate delta time
            last_time = current_time  # Update last_time for the next frame

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.paused:  # Left click to start the game or make the bird jump
                        if not self.flying:
                            self.flying = True
                            self.score = 0
                            self.bird = Bird(self.collide_sprites, self.scale_factor * 1.5)
                    
                        else:
                            self.bird.jump()

                    elif event.button == 3 and self.flying:  # Right click to pause/unpause the game
                        self.paused = not self.paused

                elif event.type == self.obstacle_timer and self.flying and not self.paused:
                    # Only create new sprites if the game is not paused and the bird is flying 
                    Pig(self.collide_sprites, self.scale_factor * 0.1)
                    Enemy_Bird(self.collide_sprites, self.scale_factor * 2.5)
                    Logs(self.collide_sprites, -1, self.scroll_speed) # bottom log
                    Logs(self.collide_sprites, 1, self.scroll_speed) # top log

                elif event.type == self.flash_text_timer:  # Flash text event handling
                    self.flash_text_active = False
                    pygame.time.set_timer(self.flash_text_timer, 0)  # Stop the timer
            
            keys = pygame.key.get_pressed()
            if self.flying and not self.paused:
                if hasattr(self, 'bird'): # initially, there is no bird so only take A and D input when the bird exists 
                    self.bird.moving_left = keys[pygame.K_a]
                    self.bird.moving_right = keys[pygame.K_d]
            
            # Display New game menu when the bird is dead
            if not self.flying: 
                self.display_surface.fill('skyblue')
                self.display_surface.blit(self.menu_surf, self.menu_rect)  
                self.draw_text_box(self.display_surface, 'yellow', 'New Game', 'red', SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 + 200)
                self.draw_text_box(self.display_surface, 'yellow', f'High Score: {self.best_score}', 'red', SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 + 300)

            # Display Pause game menu when the game is paused
            elif self.paused:
                self.display_surface.blit(self.menu_surf, self.menu_rect)  
                self.draw_text_box(self.display_surface, 'yellow', 'Resume', 'red', SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 + 200)
            
            # Update the game objects normally when the game is running 
            else: 
                self.update_game_objects(dt)
                            
            pygame.display.update()
            self.clock.tick(FRAMERATE)
            
if __name__ == '__main__':
    game =  AppMain()
    game.run()