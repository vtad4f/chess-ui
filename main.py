

from board import ChessBoard
from player import AiPlayer

if __name__ == '__main__':
   """
      BRIEF  Main execution
   """
   from PyQt5.QtCore import QThread
   from PyQt5.QtWidgets import QApplication
   
   exe_path = '../chess-ai/build/chess-ai.exe'
   total_s = 15 * 60.0
   
   q_app = QApplication([])
   thread = QThread()
   board = ChessBoard()
   # player_w = AiPlayer(exe_path, total_s, AiPlayer.WHITE, thread, board)
   player_b = AiPlayer(exe_path, total_s, AiPlayer.BLACK, thread, board)
   
   q_app.aboutToQuit.connect(thread.quit)
   thread.start()
   
   # player_w.TakeTurn(board.fen())
   
   board.show()
   q_app.exec()
   thread.wait()
   
   