#
# THIS CODE
#   Author: Vincent Allen
#
# IS A REFACTORED VERSION OF STACK OVERFLOW ANSWERS:
#   https://stackoverflow.com/questions/47287328/get-clicked-chess-piece-from-an-svg-chessboard
#   Original authors: a_manthey_67, Boštjan Mejak
#
# Also see https://github.com/niklasf/python-chess/issues/223
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
   WND_XY = 200
   
   def __init__(self):
      """
         BRIEF  Initialize the chessboard
      """
      super().__init__()
      self.setWindowTitle("Chess")
      
      self.svg_xy = 50 # top left x,y-pos of chessboard
      self.board_size = 600 # size of chessboard
      self.margin = 0.05 * self.board_size
      self.square_size  = (self.board_size - 2*self.margin) / 8.0
      wnd_wh = self.board_size + 2*self.svg_xy
      
      self.setGeometry(ChessBoard.WND_XY, ChessBoard.WND_XY, wnd_wh, wnd_wh)
      self.svg_widget = QSvgWidget(parent=self)
      self.svg_widget.setGeometry(self.svg_xy, self.svg_xy, self.board_size, self.board_size)
      
      self.last_clicked = None
      self.board = chess.Board()
      self.DrawBoard()
      
   @pyqtSlot(QWidget)
   def mousePressEvent(self, event):
      """
         BRIEF  Update the board state based on user clicks
                If the state changes, update the svg widget
      """
      if self.LeftClickedBoard(event):
         clicked_algebraic = self.GetClicked(event)
         
         if self.last_clicked:
            if self.last_clicked != clicked_algebraic:
               self.ApplyMove(self.last_clicked + clicked_algebraic)
               
         self.last_clicked = clicked_algebraic
         
   def ApplyMove(self, uci):
      """
         BRIEF  Apply a move to the board
      """
      move = chess.Move.from_uci(uci)
      if move in self.board.legal_moves:
         self.board.push(move)
         self.DrawBoard()
         
   def DrawBoard(self):
      """
         BRIEF  Redraw the chessboard based on self.board state
                Highlight src and dest squares for last move
                Highlight king if in check
      """
      self.svg_widget.load(self.board._repr_svg_().encode("utf-8"))
      print(self.board.fen())
      if self.board.is_game_over():
         print("Game over!")
      sys.stdout.flush()
      
   def GetClicked(self, event):
      """
         BRIEF  Get the algebraic notation for the clicked square
      """
      top_left = self.svg_xy + self.margin
      file =     int((event.x() - top_left)/self.square_size)
      rank = 7 - int((event.y() - top_left)/self.square_size)
      return chr(file + 97) + str(rank + 1)
      
   def LeftClickedBoard(self, event):
      """
         BRIEF  Check to see if they left-clicked on the chess board
      """
      topleft     = self.svg_xy + self.margin
      bottomright = self.board_size + self.svg_xy - self.margin
      return all([
         event.buttons() == Qt.LeftButton,
         topleft < event.x() < bottomright,
         topleft < event.y() < bottomright,
      ])
      
      
if __name__ == "__main__":
   """
      BRIEF  Test the ChessBoard class
   """
   q_app = QApplication([])
   wnd = ChessBoard()
   wnd.show()
   q_app.exec()
   
   