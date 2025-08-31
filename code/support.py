import pygame
from csv import reader
import os, sys
from settings import *

def import_csv_layout(path):
  terrain_map = []
  with open(path) as level_map:
    layout = reader(level_map, delimiter=',')
    for row in layout:
      terrain_map.append(list(row))
    return terrain_map
  
def import_folder(path):
  surface_list = []

  for _, __, img_files in os.walk(path):
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

def get_mouse_direction_status(player_rect):
  mouse_vec = pygame.math.Vector2(pygame.mouse.get_pos()) - get_camera_offset(pygame.display.get_surface(), player_rect)
  player_vec = pygame.math.Vector2(player_rect.center)
  distance = (mouse_vec - player_vec).magnitude()
  if distance > 0:
    direction = (mouse_vec-player_vec).normalize()
  else:
    direction = pygame.math.Vector2()
  
  if abs(direction.x) > abs(direction.y):
    if direction.x > 0:
      status = 'right'
    else:
      status = 'left'
  else:
    if direction.y > 0:
      status = 'down'
    else:
      status = 'up'

  return (direction, status)

class Coord:
  def __init__(self, x, y):
    self.x = x
    self.y = y

def get_marker_quadrants(marker):
  quadrant = Coord(0,0)
  quadrant.x = marker.x - 0.5
  quadrant.y = marker.y - 0.5
  
  # check if marker is in center box
  centered_marker = Coord(marker.x - 0.5, marker.y - 0.5)
  is_bound_x = abs(centered_marker.x) <= BOUNDARY_LENGTH
  is_bound_y = abs(centered_marker.y) <= BOUNDARY_LENGTH
  
  if is_bound_x and is_bound_y: quadrant = Coord(0,0)
  elif is_bound_x:
    is_bound_x = abs(centered_marker.x) <= BOUNDARY_LENGTH/5
    if is_bound_x: quadrant.x = 0
  elif is_bound_y:
    is_bound_y = abs(centered_marker.y) <= BOUNDARY_LENGTH/5
    if is_bound_y: quadrant.y = 0
  
  return quadrant
  
def get_direction_from_quadrant(quadrant):
  status = 'right'
  if abs(quadrant.x) > abs(quadrant.y):
      if quadrant.x > 0:
        status = 'right'
      else:
        status = 'left'
  else:
    if quadrant.y > 0:
      status = 'down'
    else:
      status = 'up'
  return status

def get_dpc_angle(hand_landmarks, tipid):
  # DPC - dip, pip, mcp
  pip_mcp = pygame.math.Vector2(hand_landmarks[tipid - 2].x-hand_landmarks[tipid - 3].x, hand_landmarks[tipid - 2].y-hand_landmarks[tipid - 3].y)
  dip_pip = pygame.math.Vector2(hand_landmarks[tipid - 1].x-hand_landmarks[tipid - 2].x, hand_landmarks[tipid - 1].y-hand_landmarks[tipid - 2].y)
  angle = pygame.math.Vector2.angle_to(dip_pip, pip_mcp)
  return abs(angle)

def get_scaled_marker_pos(marker_pos, img_surf, frame, scale_factor):
  offset_x = WIDTH/2 - img_surf.get_width()/2
  offset_y = HEIGHT/2 - img_surf.get_height()/2
  
  scaled_marker_pos = Coord(0, 0)
  scaled_marker_pos.x = marker_pos.x*frame.get_width()*scale_factor + offset_x
  scaled_marker_pos.y = marker_pos.y*frame.get_height()*scale_factor + offset_y
  
  return scaled_marker_pos

def resource_path(rel_path):
  try:
    base_path = sys._MEIPASS
  except AttributeError:
    base_path = os.path.abspath('..')
    
  return os.path.join(base_path, rel_path)