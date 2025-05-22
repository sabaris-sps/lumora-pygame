import pygame
from csv import reader
from os import walk

def import_csv_layout(path):
  terrain_map = []
  with open(path) as level_map:
    layout = reader(level_map, delimiter=',')
    for row in layout:
      terrain_map.append(list(row))
    return terrain_map
  
def import_folder(path):
  surface_list = []

  for _, __, img_files in walk(path):
    for image in img_files:
      full_path = path + '/' + image
      image_surface = pygame.image.load(full_path).convert_alpha()
      surface_list.append(image_surface)

  return surface_list

class Timer:
  def __init__(self, duration):
    self.acting = False
    self.action_time = None
    self.action_duration = duration

  def action_init(self):
    self.acting = True
    self.action_time = pygame.time.get_ticks()

  def can_act(self):
    return not self.acting
  
  def update(self):
    if self.acting:
      current_time = pygame.time.get_ticks()
      if current_time - self.action_time >= self.action_duration:
        self.acting = False

def get_camera_offset(display_surface, player_rect):
  # get camera offset
  half_width = display_surface.get_size()[0]//2
  half_height = display_surface.get_size()[1]//2
  offset = pygame.math.Vector2(100,300)

  offset.x = player_rect.centerx - half_width
  offset.y = player_rect.centery - half_height
  offset_pos = - pygame.math.Vector2(0,40) - offset

  return offset_pos