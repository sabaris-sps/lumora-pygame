import pygame,sys
from settings import *
from level import Level

class Game:
  def __init__(self):

    pygame.init()
    self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption('ZELDA')
    self.clock = pygame.time.Clock()
    self.level = Level()

    # sound
    main_sound = pygame.mixer.Sound('../audio/main.ogg')
    main_sound.set_volume(0.2)
    main_sound.play(loops= -1)

  def run(self):
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
            self.level.toggle_menu('upgrade')
          if event.key == pygame.K_i:
            self.level.toggle_menu('inventory')
      
      self.screen.fill(WATER_COLOR)
      self.level.run()
      pygame.display.update()
      self.clock.tick(FPS)
    
if __name__ == '__main__':
  game = Game()
  game.run()