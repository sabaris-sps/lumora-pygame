import pygame
from settings import *
from support import *

class Inventory_Bar:
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
    object_image = pygame.image.load(resource_path(f'graphics/inventory-view/{object_id}.png')).convert_alpha()
    x = index*self.box_size + self.left
    y = self.top
    object_rect = object_image.get_rect(topleft = (x,y)).inflate(-10,-10)

    self.display_surface.blit(object_image, object_rect)

    # text setup
    text_surf = self.font.render(str(value), False, TEXT_COLOR)
    text_rect = text_surf.get_rect(bottomright = (x + self.box_size, y + self.box_size - 10))
    self.display_surface.blit(text_surf, text_rect)
  
  def show_grass(self, value, index):
    grass_image = pygame.image.load(resource_path(f'graphics/grass/grass_1.png')).convert_alpha()
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

    self.show_object(4, player.inventory['tree'], 0)
    self.show_grass(player.inventory['grass'], 1)

    pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.bg_rect, 3)


class Inventory:
  def __init__(self, player):
    
    # general setup
    self.display_surface = pygame.display.get_surface()
    self.player = player
    self.attribute_nr = len(player.stats)
    self.attribute_names = list(player.stats.keys())
    self.max_values = list(self.player.max_stats.values())
    self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

    # item creation
    self.height = self.display_surface.get_size()[1] * 0.8
    self.width =  self.display_surface.get_size()[0] // (self.attribute_nr+1) # +1 => width used in padding
    self.create_item()

    # selection system
    self.selection_index = 0
    self.selection_time = None
    self.selection_duration = 200
    self.can_move = True

  def input(self):
    keys = pygame.key.get_pressed()

    if self.can_move:
      if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
        self.selection_index += 1
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()
      elif keys[pygame.K_LEFT]  and self.selection_index > 0:
        self.selection_index -= 1
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()

      if keys[pygame.K_SPACE]:
        self.can_move = False
        self.selection_time = pygame.time.get_ticks()
        self.item_list[self.selection_index].trigger(self.player)

  def selection_cooldown(self):
    if not self.can_move:
      current_time = pygame.time.get_ticks()
      if current_time - self.selection_time >= self.selection_duration:
        self.can_move = True

  def create_item(self):
    self.item_list = []

    for index  in range(self.attribute_nr):
      full_width = self.display_surface.get_size()[0]
      increment = full_width // self.attribute_nr
      left = (index * increment) + (increment - self.width)//2

      top = self.display_surface.get_size()[1] * 0.1

      item = Item(left, top, self.width, self.height, index, self.font)
      self.item_list.append(item)

  def display(self):
    self.input()
    self.selection_cooldown()

    for index, item in enumerate(self.item_list):
      name = self.attribute_names[index]
      value = list(self.player.stats.values()) [index]
      max_value = self.max_values[index]
      cost = list(self.player.upgrade_cost.values())[index]
      item.display(self.display_surface, self.selection_index, name, value, max_value, cost)


class Item:
  def __init__(self, l,t,w,h,index, font):
    self.rect = pygame.Rect(l,t,w,h)
    self.index = index
    self.font = font

  def trigger(self, player):
    upgrade_attribute = list(player.inventory.keys())[self.index]

    if player.exp >= player.upgrade_cost[upgrade_attribute] and player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]:
      player.exp -= player.upgrade_cost[upgrade_attribute]
      player.stats[upgrade_attribute] *= 1.2
      player.upgrade_cost[upgrade_attribute] *= 1.4

    if player.stats[upgrade_attribute] > player.max_stats[upgrade_attribute]:
      player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

  def display_names(self, surface, name, cost, selected):
    color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

    # title
    title_surf = self.font.render(name, False, color)
    title_rect = title_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0,20))

    # cost
    cost_surf = self.font.render(str(int(cost)), False, color)
    cost_rect = title_surf.get_rect(midbottom = self.rect.midbottom - pygame.math.Vector2(0,20))

    # draw
    surface.blit(title_surf, title_rect)
    surface.blit(cost_surf, cost_rect)

  def display_bar(self, surface, value, max_value, selected):

    # drawing setup
    top = self.rect.midtop + pygame.math.Vector2(0,60)
    bottom = self.rect.midbottom - pygame.math.Vector2(0,60)
    color = BAR_COLOR_SELECTED if selected else BAR_COLOR

    # bar setup
    full_height = bottom[1] - top[1]
    relative_number = (value / max_value) * full_height
    value_rect = pygame.Rect(top[0]-15, bottom[1] - relative_number, 30, 30)

    # draw elements
    pygame.draw.line(surface, color, top, bottom, 5)
    pygame.draw.rect(surface, color, value_rect)

  def display(self,surface, selection_num, name, value, max_value, cost):
    selected = selection_num == self.index
    if selected:
      pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
      pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
    else:
      pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
      pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

    self.display_names(surface, name, cost, selected)
    self.display_bar(surface, value, max_value, selected)