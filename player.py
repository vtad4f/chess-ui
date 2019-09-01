

from PyQt5.QtCore import pyqtSlot
from subprocess import Popen, PIPE, DEVNULL
import sys


class AiPlayer():
   """
      BRIEF  A wrapper for an AI executable
   """
   
   def __init__(self, exe_path, turn_limit_s):
      """
         BRIEF  Start with the path to the exe and seconds limit per turn
      """
      self.exe_path = exe_path
      self.turn_limit_s = turn_limit_s
      
   def TakeTurn(self, fen):
      """
         BRIEF  Open a process to get the next move from the AI
      """
      args = [exe_path, fen, str(self.turn_limit_s)]
      process = Popen(args,stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
      out, _ = process.communicate()
      return out.decode().rstrip('\r\n')
      
      
if __name__ == "__main__":
   """
      BRIEF  Test the Player class
   """
   exe_path = '../chess-ai/build/chess-ai.exe'
   
   player1 = AiPlayer(exe_path, '.1')
   player2 = AiPlayer(exe_path, '.1')
   player = player1
   
   import chess
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
   
   