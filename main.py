#
# MERGED TWO SOLUTIONS FROM:
#   https://stackoverflow.com/questions/47287328/get-clicked-chess-piece-from-an-svg-chessboard
#

import chess
import chess.svg
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
import sys


class ChessBoard(QWidget):
   """
      BRIEF  An interactive chessboard that only allows legal moves
   """
   
   def __init__(self):
      """
      Initialize the chessboard.
      """
      super().__init__()
      
      self.setGeometry(300, 300, 800, 800)
      
      self.svg_widget = QSvgWidget(parent=self)
      self.svg_x = 50 # top left x-pos of chessboard
      self.svg_y = 50 # top left y-pos of chessboard
      self.board_size = 600 # size of chessboard
      self.svg_widget.setGeometry(self.svg_x, self.svg_y, self.board_size, self.board_size)
      
      self.margin = 0.05 * self.board_size
      self.square_size  = (self.board_size - 2 * self.margin) / 8.0
      
      self.last_clicked = None
      self.board = chess.Board()
      self.DrawBoard()
      
   @pyqtSlot(QWidget)
   def mousePressEvent(self, event):
      """
      Handle left mouse clicks and enable moving chess pieces by
      clicking on a chess piece and then the target square.

      Moves must be made according to the rules of chess because
      illegal moves are suppressed.
      """
      if self.LeftClickedBoard(event):
         clicked_piece, clicked_algebraic = self.GetClicked(event)
         
         if self.last_clicked:
            last_piece, last_algebraic = self.last_clicked
            move = chess.Move.from_uci(last_algebraic + clicked_algebraic)
            if move in self.board.legal_moves:
               self.board.push(move)
               self.DrawBoard()
            self.last_clicked = None
            
         self.last_clicked = (clicked_piece, clicked_algebraic)
         
   def GetClicked(self, event):
      """
      """
      file      =     int((event.x() - (self.svg_x + self.margin))/self.square_size)
      rank      = 7 - int((event.y() - (self.svg_y + self.margin))/self.square_size)
      square    = chess.square(file, rank) # TODO - chess.sqare.mirror() if white is on top
      piece     = self.board.piece_at(square)
      algebraic = chr(file + 97) + str(rank + 1)
      return piece, algebraic
      
   def LeftClickedBoard(self, event):
      """
      """
      return all([
         event.buttons() == Qt.LeftButton,
         self.svg_x               < event.x() <= self.svg_x + self.board_size,
         self.svg_y               < event.y() <= self.svg_y + self.board_size,
         self.svg_x + self.margin < event.x() <  self.svg_x + self.board_size - self.margin,
         self.svg_y + self.margin < event.y() <  self.svg_y + self.board_size - self.margin,
      ])
      
   def DrawBoard(self):
      """
         BRIEF  Redraw the chessboard based on self.board state
                Highlight src and dest squares for last move
                Highlight king if in check
      """
      self.svg_widget.load(self.board._repr_svg_().encode("UTF-8"))
      print(self.board.fen())
      if self.board.is_game_over():
         print("Game over!")
      sys.stdout.flush()
      
      
if __name__ == "__main__":
   """
   """
   q_app = QApplication([])
   wnd = ChessBoard()
   wnd.setWindowTitle("Chess")
   wnd.show()
   q_app.exec()
   
   