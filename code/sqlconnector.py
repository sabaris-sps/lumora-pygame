import mysql.connector
from settings import *

class SQL:
  def __init__(self):
    self.conn = mysql.connector.connect(**DB_CONFIG)
    self.cursor = self.conn.cursor()
    
  def create_table(self):
    query = """
    CREATE TABLE IF NOT EXISTS USER_HISTORY (
      id INT AUTO_INCREMENT PRIMARY KEY,
      exp INT,
      stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    self.cursor.execute(query)    
    
  def add_score(self, exp):
    query = "INSERT INTO USER_HISTORY (exp) VALUES(%s)"
    vals = (int(exp),)
    self.cursor.execute(query, vals)
    self.conn.commit()
  
  def get_records(self):
    query = "SELECT * FROM USER_HISTORY"
    self.cursor.execute(query)
    records = self.cursor.fetchall()
    return records
    
  def close_conn(self):
    if self.cursor:
      self.cursor.close()
    if self.conn:
      self.conn.close()