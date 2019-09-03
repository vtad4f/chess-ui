

from board import ChessBoard
from player import AiPlayer

if __name__ == '__main__':
   """
      BRIEF  Main execution
   """
   from PyQt5.QtCore import QThread
   from PyQt5.QtWidgets import QApplication
   
   q_app = QApplication([])
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   
   player_w = AiPlayer(AiPlayer.WHITE, exe_path, 5)
   player_b = AiPlayer(AiPlayer.BLACK, exe_path, 5)
   board = ChessBoard()
   
   thread = QThread()
   player_w.moveToThread(thread)
   player_b.moveToThread(thread)
   
   player_w.DecidedMove.connect(board.ApplyMove)
   player_b.DecidedMove.connect(board.ApplyMove)
   board.ReadyForNextMove.connect(player_w.TakeTurn)
   board.ReadyForNextMove.connect(player_b.TakeTurn)
   q_app.aboutToQuit.connect(thread.quit)
   
   thread.start()
   player_w.TakeTurn(board.fen())
   
   board.show()
   q_app.exec()
   thread.wait()
   
   