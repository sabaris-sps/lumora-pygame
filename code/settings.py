import os,sys

def resource_path(rel_path):
  try:
    base_path = sys._MEIPASS
  except AttributeError:
    base_path = os.path.abspath('..')
    
  return os.path.join(base_path, rel_path)

# game setup
WIDTH    = 1280	
HEIGHT   = 720
FPS      = 60
TILESIZE = 64
HITBOX_OFFSET = {
    'player': -26,
    'object': -40,
    'grass': -10,
    'invisible': 0}
object_id = {
  'tree': 4,
}
ATTACK_RADIUS = (TILESIZE * 0.8,TILESIZE*0.8)
BOUNDARY_LENGTH = 1/56

# UI
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ATTACK_POWER_WIDTH = 120
ITEM_BOX_SIZE = 80
UI_FONT = resource_path('graphics/font/joystix.ttf')
UI_FONT_SIZE = 18

# ui colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
ATTACK_POWER_COLOR = 'purple'
UI_BORDER_COLOR_ACTIVE = 'gold'

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

# weapons 
weapon_data = {
    'sword': {'cooldown': 100, 'damage': 15,'graphic':resource_path('graphics/weapons/sword/full.png')},
    'lance': {'cooldown': 400, 'damage': 30,'graphic':resource_path('graphics/weapons/lance/full.png')},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic':resource_path('graphics/weapons/axe/full.png')},
    'rapier':{'cooldown': 50, 'damage': 8, 'graphic':resource_path('graphics/weapons/rapier/full.png')},
    'sai':{'cooldown': 80, 'damage': 10, 'graphic':resource_path('graphics/weapons/sai/full.png')}}

# magic
magic_data = {
    'flame': {'strength': 5,'cost': 10,'graphic':resource_path('graphics/particles/flame/fire.png')},
    'heal' : {'strength': 20,'cost': 10,'graphic':resource_path('graphics/particles/heal/heal.png')}}

# enemy
monster_data = {
    'squid': {'health': 100,'exp':100,'damage':10,'attack_type': 'slash', 'attack_sound':resource_path('audio/attack/slash.wav'), 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
    'raccoon': {'health': 300,'exp':250,'damage':15,'attack_type': 'claw',  'attack_sound':resource_path('audio/attack/claw.wav'),'speed': 2, 'resistance': 3, 'attack_radius': 120, 'notice_radius': 400},
    'spirit': {'health': 100,'exp':110,'damage':8,'attack_type': 'thunder', 'attack_sound':resource_path('audio/attack/fireball.wav'), 'speed': 4, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
    'bamboo': {'health': 70,'exp':120,'damage':6,'attack_type': 'leaf_attack', 'attack_sound':resource_path('audio/attack/slash.wav'), 'speed': 3, 'resistance': 3, 'attack_radius': 50, 'notice_radius': 300}}

# SQL setup
DB_CONFIG = {
  'host': 'localhost',
  'user': 'root',
  'password': '0110',
  'database': 'lumora_test'
}