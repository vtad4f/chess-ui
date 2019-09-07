

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
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
   
   RequestFen = pyqtSignal()
   
   def __init__(self, exe_path, turn_limit_s, color, thread = None, board = None):
      """
         BRIEF  Start with the path to the exe and seconds limit per turn
      """
      super().__init__(color, thread, board)
      
      # set member vars
      self.exe_path = exe_path
      self.turn_limit_s = turn_limit_s
      self.enabled = False
      
      # connect signals/slots
      if board:
         self.RequestFen.connect(board.TriggerNextMove)
         
   def IsMyMove(self, fen):
      """
      """
      return super().IsMyMove(fen) and self.enabled
      
   @pyqtSlot(str)
   def TakeTurn(self, fen):
      """
         BRIEF   Open a process to get the next move from the AI
                 Emit DecidedMove(uci) and return uci
      """
      if self.IsMyMove(fen):
         
         # run the process
         args = [self.exe_path, fen, str(self.turn_limit_s)]
         process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
         out, _ = process.communicate()
         
         # emit and return the move
         uci = out.decode().rstrip('\r\n')
         self.DecidedMove.emit(uci)
         return uci
         
   @pyqtSlot(int)
   def Checked(self, check_state):
      """
      """
      self.Enable(check_state == Qt.Checked)
      
   @pyqtSlot(bool)
   def Enable(self, enabled):
      """
      """
      self.enabled = enabled
      self.RequestFen.emit()
      
      
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
   player_w = AiPlayer(exe_path, .1, Player.WHITE)
   player_b = AiPlayer(exe_path, .1, Player.BLACK)
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
         sys.stdout.flush()
         
         move = chess.Move.from_uci(uci)
         assert(move in self.legal_moves)
         self.push(move)
         
         if self.is_game_over():
            print(self.fen())
            sys.stdout.flush()
            self.GameOver.emit()
         else:
            self.ReadyForNextMove.emit(self.fen())
            
   q_app = QApplication([])
   thread = QThread()
   board = ChessBoard()
   player_w = AiPlayer(exe_path, .1, Player.WHITE, thread, board)
   player_b = AiPlayer(exe_path, .1, Player.BLACK, thread, board)
   
   board.GameOver.connect(q_app.exit)
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   player_w.TakeTurn(board.fen())
   
   q_app.exec()
   thread.wait()
   
   