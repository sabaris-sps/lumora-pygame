import pygame
import mediapipe as mp

class Detector:
  def __init__(self):
    self.face_mesh_mp = mp.solutions.face_mesh
    self.face_mesh = self.face_mesh_mp.FaceMesh(static_image_mode = False, refine_landmarks=True)
    self.hands_mp = mp.solutions.hands
    self.hands = self.hands_mp.Hands(static_image_mode = False)
    
  def get_marker_pos(self, frame):
    self.face_res = self.face_mesh.process(frame)
    if self.face_res.multi_face_landmarks:
      marker = self.face_res.multi_face_landmarks[2].landmark[1] # 1 - Tip of nose
      return marker
    return None
  
  def get_hand_status(self, frame, hand_id=-1):
    self.get_hand_marker(frame)
    tip_ids = [8,12,16,20]
    res_motions = []
    if self.hand_res.multi_hand_landmarks:
      hand_landmarks = self.hand_res.multi_hand_landmarks[hand_id].landmark
      
      is_index_up = hand_landmarks[8].y <= hand_landmarks[7].y
      is_four_up = all([hand_landmarks[tip_id].y <= hand_landmarks[tip_id - 1].y for tip_id in tip_ids])
      mcp_wrist = pygame.math.Vector2(hand_landmarks[2].x - hand_landmarks[0].x, hand_landmarks[2].y - hand_landmarks[0].y)
      tip_mcp = pygame.math.Vector2(hand_landmarks[4].x - hand_landmarks[2].x, hand_landmarks[4].y - hand_landmarks[2].y)
      angle = pygame.math.Vector2.angle_to(tip_mcp, mcp_wrist)
      is_thumb_out = abs(angle) < 10.0 # For right hand
      
      if is_four_up and is_thumb_out:
        res_motions.append('magic')
        res_motions.append('move')
      elif is_four_up and not is_thumb_out:
        res_motions.append('magic')
      else:
        if is_index_up:
          res_motions.append('move')
        if is_thumb_out:
          res_motions.append('attack')
      return res_motions
    
    return None
  
  def get_hand_marker(self, frame, hand_id =-1):
    self.hand_res = self.hands.process(frame)
    if self.hand_res.multi_hand_landmarks:
      self.index_marker_pos = self.hand_res.multi_hand_landmarks[hand_id].landmark[8] # 8 - index tip
      return self.index_marker_pos