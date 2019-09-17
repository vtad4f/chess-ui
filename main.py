

from board import ChessBoard
from player import AiPlayer, PlayerUI
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout


class Window(QWidget):
   """
      BRIEF  This main window contains a chess board and player options
   """
   
   def __init__(self, exe_path, turn_limit_s, thread):
      """
         BRIEF  Set up the UI
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
   
   default_exe_path = '../chess-ai/build/chess-ai.exe'
   default_turn_limis_s = 8
   
   q_app = QApplication([])
   
   thread = QThread()
   wnd = Window(default_exe_path, default_turn_limis_s, thread)
   
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   wnd.show()
   q_app.exec()
   thread.wait()
   
   