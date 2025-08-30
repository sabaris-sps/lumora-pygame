import pygame
from settings import *
from tile import Tile, Tree
from player import Player
from weapon import Weapon
from ui import UI
from enemy import Enemy
from debug import debug
from support import *
from random import choice, randint
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from inventory import Inventory_Bar
from detector import Detector
import cv2
from display_message import DisplayMessages

class Level:
  def __init__(self):

    # get the display surface
    self.display_surface = pygame.display.get_surface()
    self.game_paused = False
    self.menu_open = None
    
    # sprite group setup
    self.visible_sprites = YSortCameraGroup()
    self.obstacle_sprites = pygame.sprite.Group()

    # attack sprites
    self.current_attack = None # weapon
    self.attack_sprites = pygame.sprite.Group()
    self.attackable_sprites = pygame.sprite.Group()

    # video detection for movement
    self.detector = Detector()
    self.cap = cv2.VideoCapture(0)
    if not self.cap.isOpened():
      print('Error opening camera')

    # sprite setup
    self.create_map()

    # user interface
    self.ui = UI()
    self.upgrade = Upgrade(self.player)

    # inventory
    self.inventory_bar = Inventory_Bar()
 
    # particles
    self.animation_player = AnimationPlayer()
    self.magic_player = MagicPlayer(self.animation_player)
    
    # display message
    self.display_messages = DisplayMessages()
    self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
  def create_map(self):
    layouts = {
      'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
      'grass': import_csv_layout('../map/map_Grass.csv'),
      'object': import_csv_layout('../map/map_Objects.csv'),
      'entities': import_csv_layout('../map/map_Entities.csv')
    }
    self.graphics = {
      'grass': import_folder('../graphics/Grass'),
      'objects': import_folder('../graphics/Objects')
    }
    
    for style,layout in layouts.items():
      for row_index, row in enumerate(layout):
        for col_index, col in enumerate(row):
          if col != '-1':
            x = col_index * TILESIZE
            y = row_index * TILESIZE
            if style == 'boundary':
              Tile((x,y), [self.obstacle_sprites], 'invisible')
            if style == 'grass':
              random_grass_image = choice(self.graphics['grass'])
              Tile(
                (x,y), 
                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 
                'grass', 
                random_grass_image)
            if style == 'object':
              surf = self.graphics['objects'][int(col)]
              if int(col) == object_id['tree']:
                Tree((x,y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'object', surf, self.tree_death_action)
              else:
                Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
            if style == 'entities':
              if col  == '394': # player coordinate
                self.player = Player(
                  (x,y), 
                  [self.visible_sprites], 
                  self.obstacle_sprites, 
                  self.create_attack, 
                  self.destroy_attack,
                  self.create_magic,
                  self.create_tree,
                  self.detector,
                  self.cap)
              else:
                if col == '390': monster_name = 'bamboo'
                elif col == '391': monster_name = 'spirit'
                elif col == '392': monster_name = 'raccoon'
                else: monster_name = 'squid'
                Enemy(
                  monster_name,
                  (x,y),
                  [self.visible_sprites, self.attackable_sprites], 
                  self.obstacle_sprites,
                  self.damage_player,
                  self.trigger_death_particles,
                  self.add_exp)

  def create_attack(self):
    self.current_attack = Weapon(self.player,[self.visible_sprites, self.attack_sprites])

  def create_magic(self, style, strength, cost):
    if style == 'heal':
      if not self.magic_player.heal(self.player, strength, cost, [self.visible_sprites]):
        self.display_messages.add('Energy not enough')
    elif style == 'flame':
      if not self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites]):
        self.display_messages.add('Energy not enough')

  def destroy_attack(self):
    if self.current_attack:
      self.current_attack.kill()
    self.current_attack = None

  def player_attack_logic(self):
    if self.attack_sprites:
      for attack_sprite in self.attack_sprites:
        collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
        if collision_sprites:
          for target_sprite in collision_sprites:
            if target_sprite.sprite_type == 'grass':
              pos = target_sprite.rect.center
              offset_pos = pygame.math.Vector2(0,75)
              for leaf in range(randint(3,6)):
                self.animation_player.create_grass_particles(pos-offset_pos, [self.visible_sprites])
              target_sprite.kill()
              self.player.inventory['grass'] += 1
            else:
              target_sprite.get_damage(self.player, attack_sprite.sprite_type)

  def damage_player(self, amount, attack_type):
    if self.player.invincibility_timer.can_act():
      self.player.health -= amount
      self.player.invincibility_timer.action_init()
      self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

  def trigger_death_particles(self, pos, particle_type):
    self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

  def tree_death_action(self, tree_surf, tree_rect):
    self.player.inventory['tree'] += 1
    self.animation_player.play_tree_cut(tree_surf, tree_rect, [self.visible_sprites])

  def create_tree(self, pos):
    graphics = import_folder('../graphics/Objects')
    Tree(pos, [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'object', graphics[object_id['tree']], self.tree_death_action)

  def add_exp(self, amount):
    self.player.exp += amount

  def toggle_menu(self, menu):
    if self.game_paused:
      self.game_paused = False
      self.menu_open = None
    elif not self.game_paused:
      self.game_paused = True
      self.menu_open = menu

  def display_game_over(self):
    screen_surf = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    screen_surf.set_alpha(200)
    screen_rect = screen_surf.get_rect()
    screen_rect.topleft = (0,0)
    
    text_surf = self.font.render("Player died. Game Over. Score: "+str(self.player.exp), False, TEXT_COLOR)
    text_rect = text_surf.get_rect(center = (WIDTH//2, HEIGHT//2))
    bg_rect = text_rect.copy()
    
    self.display_surface.blit(screen_surf, screen_rect)
    # pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
    self.display_surface.blit(text_surf, text_rect)

  def run(self):
    self.visible_sprites.custom_draw(self.player)
    self.ui.display(self.player)
    self.display_messages.update()
    self.inventory_bar.display(self.player)
    
    if self.player.health > 0:
      if self.game_paused:
        if self.menu_open == 'upgrade':
          self.upgrade.display()
        elif self.menu_open == 'inventory':
          self.inventory.display()
      else:
        if self.current_attack:
          self.current_attack.move(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
    else:
      self.display_game_over()    
      

class YSortCameraGroup(pygame.sprite.Group):
  def __init__(self):

    # general setup
    super().__init__()
    self.display_surface = pygame.display.get_surface()
    self.half_width = self.display_surface.get_size()[0]//2
    self.half_height = self.display_surface.get_size()[1]//2
    self.offset = pygame.math.Vector2(100,300)

    # creating the floor
    self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
    self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))

  def custom_draw(self, player):

    # getting the offset
    self.offset.x = player.rect.centerx - self.half_width
    self.offset.y = player.rect.centery - self.half_height

    # drawing the floor
    floor_offset_pos = self.floor_rect.topleft - self.offset
    self.display_surface.blit(self.floor_surf, floor_offset_pos)

    for sprite in sorted(self.sprites(), key= lambda sprite: sprite.rect.centery):
      offset_pos = sprite.rect.topleft - self.offset
      self.display_surface.blit(sprite.image, offset_pos) # second argument accepts coordinates | rect

  def enemy_update(self,player):
    enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
    for enemy in enemy_sprites:
      enemy.enemy_update(player)