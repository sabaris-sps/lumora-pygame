import pygame
from settings import *
from support import *
from entity import Entity
from tile import Tree

class Player(Entity):
  def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, create_tree):
    super().__init__(groups)
    self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
    self.rect = self.image.get_rect(topleft = pos)
    self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

    # graphics setup
    self.import_player_assets()
    self.status = 'down'

    # movement
    self.attacking  = False
    self.attack_cooldown = 200
    self.attack_time = None
    
    self.obstacle_sprites = obstacle_sprites

    # weapon
    self.create_attack = create_attack
    self.destroy_attack = destroy_attack
    self.weapon_index = 0
    self.weapon = list(weapon_data.keys())[self.weapon_index]
    self.weapon_switch_timer = Timer(200)

    # magic
    self.create_magic = create_magic
    self.magic_index = 0
    self.magic = list(magic_data.keys())[self.magic_index]
    self.magic_switch_timer = Timer(200)

    # stats
    self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
    self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
    self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}
    self.health = self.stats['health'] *0.25
    self.energy = self.stats['energy'] *0.8
    self.exp = 5000
    self.speed = self.stats['speed']

    # damage timer
    self.invincibility_timer = Timer(500)

    # import a sound
    self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
    self.weapon_attack_sound.set_volume(0.4)

    # inventory
    self.inventory = {'trees': 0}
    self.tree_place_timer = Timer(500)
    self.create_tree = create_tree

  def import_player_assets(self):
    character_path = '../graphics/player'
    self.animations = {'up': [],'down': [],'left': [],'right': [],
                       'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
                       'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}
    
    for animation in self.animations.keys():
      full_path = character_path + '/' + animation
      self.animations[animation] = import_folder(full_path)

  def input(self):
    keys = pygame.key.get_pressed()

    # movement input
    if keys[pygame.K_UP]:
      self.direction.y=-1
      self.status = 'up'
    elif keys[pygame.K_DOWN]:
      self.direction.y=1
      self.status = 'down'
    else:
      self.direction.y=0

    if keys[pygame.K_LEFT]:
      self.direction.x=-1
      self.status = 'left'
    elif keys[pygame.K_RIGHT]:
      self.direction.x=1
      self.status = 'right'
    else:
      self.direction.x=0

    # attack input
    if keys[pygame.K_SPACE] and not self.attacking:
      self.attacking = True
      self.attack_time = pygame.time.get_ticks()
      self.create_attack()
      self.weapon_attack_sound.play()

    # magic input
    if keys[pygame.K_RCTRL] and not self.attacking:
      self.attacking = True
      self.attack_time = pygame.time.get_ticks()
      style = self.magic
      strength = magic_data[self.magic]['strength'] + self.stats['magic']
      cost = magic_data[self.magic]['cost']
      self.create_magic(style, strength, cost)

    if keys[pygame.K_q] and self.weapon_switch_timer.can_act():
      self.weapon_switch_timer.action_init()
      if self.weapon_index < len(weapon_data.keys()) - 1:
        self.weapon_index += 1
      else:
        self.weapon_index = 0
      self.weapon = list(weapon_data.keys())[self.weapon_index]

    if keys[pygame.K_e] and self.magic_switch_timer.can_act():
      self.magic_switch_timer.action_init()
      if self.magic_index < len(magic_data.keys()) - 1:
        self.magic_index += 1
      else:
        self.magic_index = 0
      self.magic = list(magic_data.keys())[self.magic_index]

    # tree placing input
    if keys[pygame.K_t] and self.tree_place_timer.can_act() and self.inventory['trees']>0:
      self.tree_place_timer.action_init()

      # place the tree
      if self.status.split('_')[0] == 'right':
        self.create_tree(self.rect.topright, 4)
      if self.status.split('_')[0] == 'left':
        self.create_tree(self.rect.topleft + pygame.math.Vector2(-2*TILESIZE, 0), 4)
      if self.status.split('_')[0] == 'up':
        self.create_tree(self.rect.topleft + pygame.math.Vector2(0, -TILESIZE//2), 4)
      if self.status.split('_')[0] == 'down':
        self.create_tree(self.rect.bottomleft + pygame.math.Vector2(0, TILESIZE//2), 4)
      
      self.inventory['trees'] -= 1


  def get_status(self):

    # idle status
    if self.direction.x == 0 and self.direction.y == 0:
      if not 'idle' in self.status and not 'attack' in self.status:
        self.status += '_idle'

    if self.attacking:
      self.direction.x = 0
      self.direction.y = 0
      if not 'attack' in self.status:
        if 'idle' in self.status:
          self.status = self.status.replace('idle', 'attack')
        else:
          self.status += '_attack'
    else:
      if 'attack' in self.status:
        self.status = self.status.replace('_attack', '')

  def cooldowns(self):
    current_time = pygame.time.get_ticks()

    if self.attacking:
      if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
        self.attacking = False
        self.destroy_attack()
    
    self.weapon_switch_timer.update()
    self.magic_switch_timer.update()
    self.invincibility_timer.update()
    self.tree_place_timer.update()

  def animate(self):
    animation = self.animations[self.status]

    # loop over the frame index
    self.frame_index += self.animation_speed
    if self.frame_index >= len(animation):
      self.frame_index = 0

    # set the image
    self.image = animation[int(self.frame_index)]
    self.rect = self.image.get_rect(center = self.hitbox.center)

    # flicker
    if not self.invincibility_timer.can_act():
      alpha = self.wave_value()
      self.image.set_alpha(alpha)
    else:
      self.image.set_alpha(255)

  def get_full_weapon_damage(self):
    base_damage = self.stats['attack']
    weapon_damage = weapon_data[self.weapon]['damage']
    return base_damage + weapon_damage
  
  def get_full_magic_damage(self):
    base_damage = self.stats['magic']
    spell_damage = magic_data[self.magic]['strength']
    return base_damage + spell_damage

  def energy_recovery(self):
    if self.energy < self.stats['energy']:
      self.energy += 0.01 * self.stats['magic']
    else:
      self.energy = self.stats['energy']

  def update(self):
    self.input()
    self.cooldowns()
    self.get_status()
    self.animate()
    self.move(self.stats['speed'])
    self.energy_recovery()
    