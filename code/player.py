import pygame
from settings import *
from support import *
from entity import Entity
from math import sin, hypot
import cv2

class Player(Entity):
  def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, create_tree, detector, cap):
    super().__init__(groups)
    self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
    self.image_backup = self.image
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

    # attack duration
    self.attack_power = 1

    # magic
    self.create_magic = create_magic
    self.magic_index = 0
    self.magic = list(magic_data.keys())[self.magic_index]
    self.magic_switch_timer = Timer(500)

    # stats
    self.stats = {'health': 100,'energy':60,'attack': 10,'magic': 4,'speed': 5}
    self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic' : 10, 'speed': 10}
    self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic' : 100, 'speed': 100}
    self.health = self.stats['health']
    self.energy = self.stats['energy']
    self.exp = 300
    self.speed = self.stats['speed']

    # damage timer
    self.invincibility_timer = Timer(500)

    # import a sound
    self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
    self.weapon_attack_sound.set_volume(0.2)

    # inventory
    self.inventory = {'tree': 0, 'grass': 0}
    self.tree_place_timer = Timer(500)
    self.create_tree = create_tree
    self.inventory_workspace = [{'feedstock': 'grass', 'count': 5, 'product': 'tree'}]

    # roll motion
    self.roll_timer = Timer(300)
    
    # Camera input
    self.detector = detector
    self.cap = cap
    self.speed_addon = 0

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
    
    # Camera input setup
    ret, frame = self.cap.read()
    if not ret:
      print('Error reading camera')
    frame = cv2.flip(frame, 1)
    img_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pygame_frame = pygame.surfarray.make_surface(img_RGB.swapaxes(0,1))
    input_status = self.detector.get_hand_status(frame)
    self.index_quadrant = Coord(0,0)
    self.thumb_quadrant = Coord(0,0)
    self.direction = pygame.math.Vector2(0,0)
    if input_status != None:
      index_marker_pos = self.detector.hand_landmarks[8]
      thumb_marker_pos = self.detector.hand_landmarks[4]
      self.index_quadrant = get_marker_quadrants(index_marker_pos)
      self.thumb_quadrant = get_marker_quadrants(thumb_marker_pos)
      display_quadrants = [{'pos': index_marker_pos, 'color': 'blue'}]
      
      # movement input
      if 'move' in input_status and 'magic' not in input_status:
        self.speed_addon = self.speed*hypot(self.index_quadrant.x, self.index_quadrant.y)*4    
        self.direction = pygame.math.Vector2(self.index_quadrant.x, self.index_quadrant.y)
        if self.direction.magnitude() != 0:
          self.direction.normalize()
              
      # attack input
      if 'attack' in input_status and not self.attacking:
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        self.create_attack()
        self.weapon_attack_sound.play()
      
      if 'attack' in input_status or self.attacking:
        display_quadrants.append({'pos': thumb_marker_pos, 'color': 'red'})
    
      # magic input
      if 'magic' in input_status and not self.attacking:
        self.attacking = True
        self.attack_time = pygame.time.get_ticks()
        style = self.magic
        strength = magic_data[self.magic]['strength'] + self.stats['magic']
        cost = magic_data[self.magic]['cost']
        self.create_magic(style, strength, cost)
      
      self.show_camera(pygame_frame, display_quadrants)
      
      # setting standing status status
      if self.index_quadrant.x > 0:
        self.status = 'right'
      elif self.index_quadrant.x < 0:
        self.status = 'left'
      if self.index_quadrant.y > 0:
        self.status = 'down'
      elif self.index_quadrant.y < 0:
        self.status = 'up'

    # weapon switch input
    if keys[pygame.K_q] and self.weapon_switch_timer.can_act():
      self.weapon_switch_timer.action_init()
      if self.weapon_index < len(weapon_data.keys()) - 1:
        self.weapon_index += 1
      else:
        self.weapon_index = 0
      self.weapon = list(weapon_data.keys())[self.weapon_index]

    # magic switch input
    if keys[pygame.K_e] and self.magic_switch_timer.can_act():
      self.magic_switch_timer.action_init()
      if self.magic_index < len(magic_data.keys()) - 1:
        self.magic_index += 1
      else:
        self.magic_index = 0
      self.magic = list(magic_data.keys())[self.magic_index]
    
    # roll motion input
    if keys[pygame.K_LSHIFT] and self.roll_timer.can_act():
      self.roll_timer.action_init()

    # tree placing input
    if keys[pygame.K_LALT] and self.tree_place_timer.can_act() and self.inventory['tree']>0:
      self.tree_place_timer.action_init()

      # place the tree
      if self.status.split('_')[0] == 'right':
        self.create_tree(self.rect.topright)
      if self.status.split('_')[0] == 'left':
        self.create_tree(self.rect.topleft + pygame.math.Vector2(-2*TILESIZE, 0))
      if self.status.split('_')[0] == 'up':
        self.create_tree(self.rect.topleft + pygame.math.Vector2(0, -TILESIZE//2))
      if self.status.split('_')[0] == 'down':
        self.create_tree(self.rect.bottomleft + pygame.math.Vector2(0, TILESIZE//2))
      
      self.inventory['tree'] -= 1
      
    # attacking direction input
    if self.attacking:
      if hypot(self.index_quadrant.x, self.index_quadrant.y) != 0:
        self.status = get_direction_from_quadrant(self.index_quadrant) + '_attack'
      else:
        self.status = get_direction_from_quadrant(self.thumb_quadrant) + '_attack'

  def get_status(self):
    # idle status
    if self.direction.x == 0 and self.direction.y == 0:
      if not 'idle' in self.status and not 'attack' in self.status:
        self.status += '_idle'

    if self.attacking:
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
    self.roll_timer.update()

  def animate(self):
    animation = self.animations[self.status]

    # loop over the frame index
    self.frame_index += self.animation_speed
    if self.frame_index >= len(animation):
      self.frame_index = 0

    # set the image
    self.image = animation[int(self.frame_index)]
    self.image_backup = animation[int(self.frame_index)]
    self.rect = self.image.get_rect(center = self.hitbox.center)

    # flicker
    if not self.invincibility_timer.can_act():
      sin_max = 5
      sin_value = sin(pygame.time.get_ticks()/80)*sin_max
      scale_factor = sin_value + TILESIZE
      if sin_value > 0:
        self.image = pygame.transform.scale(self.image_backup, (scale_factor, scale_factor))
        if sin_value >= sin_max*0.9:
          self.image = pygame.mask.from_surface(self.image).to_surface(unsetcolor=None)
    else:
      self.image = self.image_backup

  def get_full_weapon_damage(self, damaged_rect):
    base_damage = self.stats['attack']
    weapon_damage = weapon_data[self.weapon]['damage']
    
    # change base damage based on distance of monster
    damaged_sprite_vec = pygame.math.Vector2(damaged_rect.center)
    player_vec = pygame.math.Vector2(self.rect.center)
    distance = abs((player_vec-damaged_sprite_vec).magnitude())
    
    full_damage = base_damage + weapon_damage - distance * 0.1
    
    return full_damage * self.attack_power

  def get_full_magic_damage(self, damaged_rect):
    base_damage = self.stats['magic']
    spell_damage = magic_data[self.magic]['strength']

    # change base damage based on distance of monster
    damaged_sprite_vec = pygame.math.Vector2(damaged_rect.center)
    player_vec = pygame.math.Vector2(self.rect.center)
    distance = abs((player_vec-damaged_sprite_vec).magnitude())
    
    full_damage = max(0, base_damage + spell_damage - distance * 0.008)

    return full_damage

  def energy_recovery(self):
    if self.energy < self.stats['energy']:
      self.energy += 0.01 * self.stats['magic']
    else:
      self.energy = self.stats['energy']

  def reduce_attack_power(self):
    if self.attacking:
      self.attack_power -= 1/200
    else:
      self.attack_power += 1/120
    
    if self.attack_power <= 0.005:
      self.attack_power = 0.005
    
    if self.attack_power >= 1:
      self.attack_power = 1

  def show_camera(self, frame, markers):
    scale_factor = WIDTH/frame.get_width()
    img_surf = pygame.transform.scale_by(frame, scale_factor).convert_alpha()
    img_surf.set_alpha(50)
    img_rect = img_surf.get_rect()
    img_rect.center = (WIDTH/2, HEIGHT/2)
    
    display_surface = pygame.display.get_surface()
    display_surface.blit(img_surf, img_rect)
    
    for marker in markers:
      scaled_marker_pos = get_scaled_marker_pos(marker.get('pos', (0,0)), img_surf, frame, scale_factor)
      pygame.draw.circle(display_surface, marker.get('color', 'green'), (scaled_marker_pos.x, scaled_marker_pos.y), 5)

  def update(self):
    self.input()
    self.cooldowns()
    self.get_status()
    self.animate()
    self.energy_recovery()
    self.reduce_attack_power()
    speed = self.stats['speed']
    if not self.roll_timer.can_act():
      ratio = (pygame.time.get_ticks() - self.roll_timer.action_time) / self.roll_timer.action_duration
      speed *= 1 + ratio
    self.move(speed+self.speed_addon)