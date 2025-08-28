import mediapipe as mp

class Detector:
  def __init__(self):
    self.face_mesh_mp = mp.solutions.face_mesh
    self.face_mesh = self.face_mesh_mp.FaceMesh(refine_landmarks=True)
  
  def get_marker_pos(self, frame):
    self.results = self.face_mesh.process(frame)
    if self.results.multi_face_landmarks:
      # 1 - Tip of nose
      marker = self.results.multi_face_landmarks[0].landmark[1]
      return marker
    return None