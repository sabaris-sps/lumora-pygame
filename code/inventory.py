import pygame
from settings import *

class Inventory:
  def __init__(self):
    self.display_surface = pygame.display.get_surface()
    self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
    
    self.box_size = 64
    self.nrbox = 3

    self.left = self.display_surface.get_size()[0]/2 - self.box_size * self.nrbox
    self.top = self.display_surface.get_size()[1] - self.box_size - 20
    self.bg_rect = pygame.Rect(self.left, self.top, self.box_size * self.nrbox, self.box_size)

  def show_object(self, object_id, value, index):
    # graphics
    if object_id < 10: object_id = f'0{object_id}'
    object_image = pygame.image.load(f'../graphics/inventory-view/{object_id}.png').convert_alpha()
    x = index*self.box_size + self.left
    y = self.top
    object_rect = object_image.get_rect(topleft = (x,y)).inflate(-10,-10)

    self.display_surface.blit(object_image, object_rect)

    # text setup
    text_surf = self.font.render(str(value), False, TEXT_COLOR)
    text_rect = text_surf.get_rect(bottomright = (x + self.box_size, y + self.box_size - 10))
    self.display_surface.blit(text_surf, text_rect)
  
  def show_grass(self, value, index):
    grass_image = pygame.image.load(f'../graphics/grass/grass_1.png').convert_alpha()
    x = index*self.box_size + self.left
    y = self.top
    grass_rect = grass_image.get_rect(topleft = (x,y)).inflate(-10,-10)

    self.display_surface.blit(grass_image, grass_rect)

    # text setup
    text_surf = self.font.render(str(value), False, TEXT_COLOR)
    text_rect = text_surf.get_rect(bottomright = (x + self.box_size, y + self.box_size - 10))
    self.display_surface.blit(text_surf, text_rect)

  def display(self, player):
    pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.bg_rect)

    self.show_object(4, player.inventory['trees'], 0)
    self.show_grass(player.inventory['grass'], 1)

    pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.bg_rect, 3)