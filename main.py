

from board import ChessBoard
from player import Player, AiPlayer
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QCheckBox, QDoubleSpinBox, QHBoxLayout, QVBoxLayout


class PlayerUI(QWidget):
   """
   """
   COLOR = { Player.WHITE : "White", Player.BLACK : "Black"}
   
   RequestFen = pyqtSignal(str)
   
   def __init__(self, player, parent = None):
      """
      """
      super().__init__(parent)
      
      # init UI
      enabled = QCheckBox("{0} AI".format(PlayerUI.COLOR[player.color]), self)
      turn_limit_s = QDoubleSpinBox(self)
      turn_limit_s.setValue(player.turn_limit_s)
      
      v_layout = QVBoxLayout()
      v_layout.addWidget(enabled)
      v_layout.addWidget(turn_limit_s)
      
      self.setLayout(v_layout)
      
      # connect signals/slots
      enabled.stateChanged.connect(player.SetCheckSate)
      turn_limit_s.valueChanged.connect(player.SetTurnLimit)
      
      
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
      
      player_options_b = PlayerUI(self.player_b, self)
      player_options_w = PlayerUI(self.player_w, self)
      
      v_layout = QVBoxLayout()
      v_layout.addStretch()
      v_layout.addWidget(player_options_b)
      v_layout.addStretch()
      v_layout.addWidget(player_options_w)
      v_layout.addStretch()
      
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
   
   