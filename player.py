

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QCheckBox, QDoubleSpinBox, QVBoxLayout
from subprocess import Popen, PIPE, DEVNULL


class Player(QObject):
   """
      BRIEF  This object represents a player in a chess game
             Define the required signals, slots, etc here
   """
   WHITE = 'w'
   BLACK = 'b'
   
   DecidedMove = pyqtSignal(str)
   
   def __init__(self, color, thread = None, board = None):
      """
         BRIEF  Cache the player's color
      """
      super().__init__()
         
      # set member vars
      self.color = color
      
      # maybe move to thread
      if thread:
         self.moveToThread(thread)
         
      # connect signals/slots
      if board:
         self.DecidedMove.connect(board.ApplyMove)
         board.ReadyForNextMove.connect(self.TakeTurn)
         
   def IsMyMove(self, fen):
      """
         BRUEF  Check the fen to see if it's my turn
      """
      return " {0} ".format(self.color) in fen
      
   @pyqtSlot(str)
   def TakeTurn(self, fen):
      """
         BRIEF  If self.IsMyMove, emit DecidedMove(uci) and return uci
      """
      
      
class AiPlayer(Player):
   """
      BRIEF  A wrapper for an AI executable
   """
   
   def __init__(self, exe_path, turn_limit_s, color, thread = None, board = None):
      """
         BRIEF  Start with the path to the exe and seconds limit per turn
      """
      super().__init__(color, thread, board)
      
      # set member vars
      self.exe_path = exe_path
      self.turn_limit_s = turn_limit_s
      self.enabled = board is None # enabled by default if no board
      self.last_fen = board.fen() if board else None
      
   def IsMyMove(self, fen):
      """
         BRIEF  This is how we are disabling AIs
      """
      return super().IsMyMove(fen) and self.enabled
      
   @pyqtSlot(str)
   def TakeTurn(self, fen):
      """
         BRIEF   Open a process to get the next move from the AI
                 Emit DecidedMove(uci) and return uci
      """
      self.last_fen = fen
      if self.IsMyMove(fen):
         
         # run the process
         args = [self.exe_path, fen, str(self.turn_limit_s)]
         process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
         out, _ = process.communicate()
         
         # emit and return the move
         uci = out.decode().rstrip('\r\n')
         self.DecidedMove.emit(uci)
         return uci
         
   @pyqtSlot(float)
   def SetTurnLimit(self, turn_limit_s):
      """
         BRIEF  Set the turn limit for the player
      """
      self.turn_limit_s = turn_limit_s
      
   @pyqtSlot(int)
   def SetCheckSate(self, check_state):
      """
         BRIEF  Overload SetEnabled for QCheckBox
      """
      self.SetEnabled(check_state == Qt.Checked)
      
   @pyqtSlot(bool)
   def SetEnabled(self, enabled):
      """
         BRIEF  Set the enabled state
      """
      self.enabled = enabled
      self.TakeTurn(self.last_fen)
      
      
class PlayerOptions(QWidget):
   """
      BRIEF  Stack the player options vertically in a UI
   """
   
   def __init__(self, player, parent = None):
      """
         BRIEF  Set up the UI
      """
      super().__init__(parent)
      
      # init UI
      color = { Player.WHITE : "White", Player.BLACK : "Black"}[player.color]
      ai_enabled = QCheckBox("{0} AI".format(color), self)
      turn_limit_s = QDoubleSpinBox(self)
      
      v_layout = QVBoxLayout()
      v_layout.addWidget(ai_enabled)
      v_layout.addWidget(turn_limit_s)
      
      self.setLayout(v_layout)
      
      # connect signals/slots or disable UI
      if isinstance(player, AiPlayer):
         ai_enabled.stateChanged.connect(player.SetCheckSate)
         turn_limit_s.setValue(player.turn_limit_s)
         turn_limit_s.valueChanged.connect(player.SetTurnLimit)
      else:
         ai_enabled.setEnabled(False)
         turn_limit_s.setEnabled(False)
         
         
if __name__ == "__main__":
   """
      BRIEF  Test the Player class
   """
   import chess
   import sys
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   
   #----------------------
   # Synchronous
   #----------------------
   board = chess.Board()
   player_b = AiPlayer(exe_path, .1, Player.BLACK)
   player_w = AiPlayer(exe_path, .1, Player.WHITE)
   player = player_w
   
   while not board.is_game_over():
      uci = player.TakeTurn(board.fen())
      
      print(uci)
      sys.stdout.flush()
      
      board.push(chess.Move.from_uci(uci))
      
      if player == player_w:
         player = player_b
      else:
         player = player_w
         
   print(board.fen())
   sys.stdout.flush()
   
   #----------------------
   # Asynchronous
   #----------------------
   from PyQt5.QtCore import QThread
   from PyQt5.QtWidgets import QApplication
   
   class ChessBoard(QObject, chess.Board):
      """
         BRIEF  A helper class for the signal/slot testing
      """
      ReadyForNextMove = pyqtSignal(str)
      GameOver = pyqtSignal()
      
      def __init__(self):
         """
            BRIEF  Construct the base classes
         """
         super().__init__()
         
      @pyqtSlot(str)
      def ApplyMove(self, uci):
         """
            BRIEF  Apply a move to the board
         """
         print(uci)
         
         move = chess.Move.from_uci(uci)
         if move in self.legal_moves:
            self.push(move)
            
            if not self.is_game_over():
               self.ReadyForNextMove.emit(self.fen())
            else:
               print(self.fen())
               self.GameOver.emit()
               
         sys.stdout.flush()
         
   q_app = QApplication([])
   thread = QThread()
   board = ChessBoard()
   player_b = AiPlayer(exe_path, .1, Player.BLACK, thread, board)
   player_w = AiPlayer(exe_path, .1, Player.WHITE, thread, board)
   
   player_options_b = PlayerOptions(player_b)
   player_options_b.setGeometry(300, 300, 200, 100)
   
   player_options_w = PlayerOptions(player_w)
   player_options_w.setGeometry(300, 600, 200, 100)
   
   board.GameOver.connect(q_app.exit)
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   player_options_b.show()
   player_options_w.show()
   
   q_app.exec()
   thread.wait()
   
   