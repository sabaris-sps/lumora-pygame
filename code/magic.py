import pygame
from settings import *
from random import randint
from support import *

class MagicPlayer:
  def __init__(self, animation_player):
    self.animation_player = animation_player
    self.sounds = {
      'heal': pygame.mixer.Sound('../audio/heal.wav'),
      'flame': pygame.mixer.Sound('../audio/fire.wav')
    }

  def heal(self, player, strength, cost, groups):
    if player.energy >= cost:
      self.sounds['heal'].play()
      player.health += strength
      player.energy -= cost
      if player.health >= player.stats['health']:
        player.health = player.stats['health']
      self.animation_player.create_particles('aura', player.rect.center, groups)
      self.animation_player.create_particles('heal', player.rect.center + pygame.math.Vector2(0,-40), groups)
      return True
    else:
      return False
      

  def flame(self, player, cost, groups):
    if player.energy >= cost:
      player.energy -= cost
      self.sounds['flame'].play()

      # direction = get_mouse_direction_status(player.rect)[0]
      direction = pygame.math.Vector2(player.quadrant.x, player.quadrant.y)
      if direction.magnitude() !=0:
        direction = direction.normalize()

        for i in range(1,6):
          offset_x = (i * direction * TILESIZE).x
          offset_y = (i * direction * TILESIZE).y
          x = player.rect.centerx + offset_x + randint(-TILESIZE//3, TILESIZE//3)
          y = player.rect.centery + offset_y + randint(-TILESIZE//3, TILESIZE//3)
          self.animation_player.create_particles('flame', (x,y), groups)
      return True
    else:
      return False