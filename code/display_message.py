import pygame
from settings import *

class DisplayMessages:
  def __init__(self):
    self.message_cooldown = 500
    self.display_messages = []
    
  def add(self, message_text):
    self.display_messages.append(DisplayMessage(message_text))
    
  def update(self):
    if self.display_messages:
      if pygame.time.get_ticks() - self.display_messages[0].created_time >= self.message_cooldown:
        self.display_messages.pop(0)
    if self.display_messages:
      for id, message in enumerate(self.display_messages):
        top = 10
        if id > 0:
          top = self.display_messages[id-1].text_rect.top + self.display_messages[-1].text_rect.height + 10
          
        message.display(top)


class DisplayMessage:
  def __init__(self, message_text, right=WIDTH-10, top = 10):
    
    # general setup
    self.display_surface = pygame.display.get_surface()
    self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
    self.message_text = message_text
    self.right = right
    
    self.text_surf = self.font.render(self.message_text, False, TEXT_COLOR)
    self.text_rect = self.text_surf.get_rect(topright = (top, self.right))
    
    self.created_time = pygame.time.get_ticks()
    
  def display(self, top):
    self.text_rect.topright = (self.right, top) # it is always (right, top)
    self.bg_rect = self.text_rect.copy()
    
    pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.bg_rect)
    self.display_surface.blit(self.text_surf, self.text_rect)
    return self.text_rect    