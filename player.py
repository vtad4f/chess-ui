

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from subprocess import Popen, PIPE, DEVNULL
from time import time


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
      self.color = color
      if thread:
         self.moveToThread(thread)
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
   
   def __init__(self, exe_path, total_s, color, thread = None, board = None):
      """
         BRIEF  Start with the path to the exe and seconds limit per turn
      """
      super().__init__(color, thread, board)
      self.exe_path = exe_path
      self.total_s = total_s
      self.remaining_s = self.total_s
      
   @pyqtSlot(str)
   def TakeTurn(self, fen):
      """
         BRIEF   Open a process to get the next move from the AI
                 Emit DecidedMove(uci) and return uci
      """
      if self.IsMyMove(fen):
         before_turn = time()
         
         args = [self.exe_path, fen, str(self.remaining_s)]
         process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
         out, _ = process.communicate()
         uci = out.decode().rstrip('\r\n')
         self.DecidedMove.emit(uci)
         
         self.remaining_s -= (time() - before_turn)
         if self.remaining_s < 0.0:
            self.remaining_s = 0.0
            
         return uci
         
         
if __name__ == "__main__":
   """
      BRIEF  Test the Player class
   """
   import chess
   import sys
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   total_s = 1
   
   #----------------------
   # Synchronous
   #----------------------
   board = chess.Board()
   player_w = AiPlayer(exe_path, total_s, Player.WHITE)
   player_b = AiPlayer(exe_path, total_s, Player.BLACK)
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
   player_w = AiPlayer(exe_path, total_s, Player.WHITE, thread, board)
   player_b = AiPlayer(exe_path, total_s, Player.BLACK, thread, board)
   
   board.GameOver.connect(q_app.exit)
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   player_w.TakeTurn(board.fen())
   
   q_app.exec()
   thread.wait()
   
   