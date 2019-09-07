

from board import ChessBoard
from player import Player, AiPlayer
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout


class PlayerUI(QCheckBox):
   """
   """
   COLOR = { Player.WHITE : "White", Player.BLACK : "Black"}
   
   RequestFen = pyqtSignal(str)
   
   def __init__(self, player, parent = None):
      """
      """
      label = "{0} AI".format(PlayerUI.COLOR[player.color])
      super().__init__(label, parent)
      
      # connect signals/slots
      self.stateChanged.connect(player.Checked)
      
      
class Window(QWidget):
   """
   """
   
   def __init__(self, exe_path, turn_limit_s, thread):
      """
      """
      super().__init__()
      
      self.board = ChessBoard(self)
      self.player_b = AiPlayer(exe_path, turn_limit_s, AiPlayer.BLACK, thread, self.board)
      self.player_w = AiPlayer(exe_path, turn_limit_s, AiPlayer.WHITE, thread, self.board)
      
      self.player_options_b = PlayerUI(self.player_b, self)
      self.player_options_w = PlayerUI(self.player_w, self)
      
      v_layout = QVBoxLayout()
      v_layout.addWidget(self.player_options_b)
      v_layout.addWidget(self.player_options_w)
      
      h_layout = QHBoxLayout()
      h_layout.addWidget(self.board)
      h_layout.addLayout(v_layout)
      h_layout.addSpacing(50)
      
      self.setLayout(h_layout)
      
      
if __name__ == '__main__':
   """
      BRIEF  Main execution
   """
   from PyQt5.QtCore import QThread
   from PyQt5.QtWidgets import QApplication
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   turn_limis_s = 1
   
   q_app = QApplication([])
   
   thread = QThread()
   wnd = Window(exe_path, turn_limis_s, thread)
   
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   wnd.show()
   q_app.exec()
   thread.wait()
   
   