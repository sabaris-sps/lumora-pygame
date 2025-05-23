import pygame
from settings import *
from support import Timer

class Tile(pygame.sprite.Sprite):
  def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
    super().__init__(groups)
    self.sprite_type = sprite_type
    y_offset = HITBOX_OFFSET[sprite_type]
    self.image = surface
    if sprite_type == 'object':
      # do an offset
      self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE)) # all objects are double (x/y) the normal size
    else:
      self.rect = self.image.get_rect(topleft = pos)
    self.hitbox = self.rect.inflate(0, y_offset
    )

class Tree(Tile):
  def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE)), tree_death_action = None):
    super().__init__(pos, groups, sprite_type, surface)

    self.health = 200
    self.is_invincible_timer = Timer(200)
    self.tree_death_action = tree_death_action
  
  def get_damage(self, player ,attack_type):
    if self.is_invincible_timer.can_act():
      if attack_type == 'weapon':
        self.health -= player.get_full_weapon_damage(self.rect)
      elif attack_type == 'magic':
        self.health -= player.get_full_magic_damage(self.rect)
      self.is_invincible_timer.action_init()

  def check_death(self):
    if self.health <= 0:
      self.tree_death_action(self.image, self.rect)
      self.kill()

  def cooldowns(self):
    self.is_invincible_timer.update()

  def update(self):
    self.check_death()
    self.cooldowns()