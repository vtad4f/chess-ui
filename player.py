

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from subprocess import Popen, PIPE, DEVNULL


class Player(QObject):
   """
      BRIEF  This object represents a player in a chess game
             Define the required signals, slots, etc here
   """
   WHITE = 'w'
   BLACK = 'b'
   
   DecidedMove = pyqtSignal(str)
   
   def __init__(self, color):
      """
         BRIEF  Cache the player's color
      """
      super().__init__()
      self.color = color
      
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
   
   def __init__(self, color, exe_path, turn_limit_s):
      """
         BRIEF  Start with the path to the exe and seconds limit per turn
      """
      super().__init__(color)
      self.exe_path = exe_path
      self.turn_limit_s = turn_limit_s
      
   @pyqtSlot(str)
   def TakeTurn(self, fen):
      """
         BRIEF   Open a process to get the next move from the AI
                 Emit DecidedMove(uci) and return uci
      """
      if self.IsMyMove(fen):
         args = [exe_path, fen, str(self.turn_limit_s)]
         process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
         out, _ = process.communicate()
         uci = out.decode().rstrip('\r\n')
         self.DecidedMove.emit(uci)
         return uci
         
         
if __name__ == "__main__":
   """
      BRIEF  Test the Player class
   """
   import chess
   import sys
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   
   player1 = AiPlayer(Player.WHITE, exe_path, '.1')
   player2 = AiPlayer(Player.BLACK, exe_path, '.1')
   
   #----------------------
   # Synchronous
   #----------------------
   player = player1
   board = chess.Board()
   
   while not board.is_game_over():
      uci = player.TakeTurn(board.fen())
      
      print(uci)
      sys.stdout.flush()
      
      board.push(chess.Move.from_uci(uci))
      
      if player == player1:
         player = player2
      else:
         player = player1
         
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
   
   player = player1
   board = ChessBoard()
   
   thread = QThread()
   player1.moveToThread(thread)
   player2.moveToThread(thread)
   
   player1.DecidedMove.connect(board.ApplyMove)
   player2.DecidedMove.connect(board.ApplyMove)
   board.ReadyForNextMove.connect(player1.TakeTurn)
   board.ReadyForNextMove.connect(player2.TakeTurn)
   board.GameOver.connect(thread.quit)
   board.GameOver.connect(q_app.exit)
   
   thread.start()
   player.TakeTurn(board.fen())
   
   q_app.exec()
   thread.wait()
   
   