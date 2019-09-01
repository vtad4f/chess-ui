

from PyQt5.QtCore import pyqtSlot
from subprocess import Popen, PIPE, DEVNULL
import sys


class Player():
   """
   """
   TURN_TIME_LIMIT_S = 1
   
   def __init__(self, exe_path = ''):
      """
      """
      self.exe_path = exe_path
      self.is_human = (exe_path == '')
      
   @pyqtSlot(str)
   def Move(self, fen):
      """
      """
      p = Popen([self.exe_path, fen, str(Player.TURN_TIME_LIMIT_S)], stdout=PIPE, stderr=DEVNULL)
      out, err = p.communicate()
      p.wait()
      print(out)
      sys.stdout.flush()
      
      
      
      
if __name__ == "__main__":
   """
      BRIEF  Test the Player class
   """
   exe_path = '../chess-ai/build/chess-ai.exe'
   player = Player(exe_path)
   player.Move('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -')
   
   