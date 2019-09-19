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
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QDialog, QWidget, QRadioButton, QPushButton, QButtonGroup, QGroupBox, QHBoxLayout, QVBoxLayout
import sys


class ChessBoard(QWidget, chess.Board):
   """
      BRIEF  An interactive chessboard that only allows legal moves
   """
   
   ReadyForNextMove = pyqtSignal(str)
   GameOver = pyqtSignal()
   
   def __init__(self, parent = None):
      """
         BRIEF  Initialize the chessboard
      """
      super().__init__(parent)
      self.setWindowTitle("Chess")
      
      self.svg_xy = 50 # top left x,y-pos of chessboard
      self.board_size = 600 # size of chessboard
      self.margin = 0.05 * self.board_size
      self.square_size  = (self.board_size - 2*self.margin) / 8.0
      wnd_wh = self.board_size + 2*self.svg_xy
      
      self.setMinimumSize(wnd_wh, wnd_wh)
      self.svg_widget = QSvgWidget(parent=self)
      self.svg_widget.setGeometry(self.svg_xy, self.svg_xy, self.board_size, self.board_size)
      
      self.last_click = None
      self.DrawBoard()
      
   @pyqtSlot(QWidget)
   def mousePressEvent(self, event):
      """
         BRIEF  Update the board state based on user clicks
                If the state changes, update the svg widget
      """
      if self.LeftClickedBoard(event):
         this_click = self.GetClicked(event)
         
         if self.last_click:
            if self.last_click != this_click:
               uci = self.last_click + this_click
               self.ApplyMove(uci + self.GetPromotion(uci))
               
         self.last_click = this_click
         
   def GetPromotion(self, uci):
      """
         BRIEF  Get the uci piece type the pawn will be promoted to
      """
      if chess.Move.from_uci(uci + 'q') in self.legal_moves:
         dialog = PromotionDialog(self)
         if dialog.exec() == QDialog.Accepted:
            return dialog.SelectedPiece()
      return ''
      
   @pyqtSlot(str)
   def ApplyMove(self, uci):
      """
         BRIEF  Apply a move to the board
      """
      move = chess.Move.from_uci(uci)
      if move in self.legal_moves:
         self.push(move)
         self.DrawBoard()
         
         print(self.fen())
         if not self.is_game_over():
            self.ReadyForNextMove.emit(self.fen())
         else:
            print("Game over!")
            self.GameOver.emit()
         sys.stdout.flush()
         
   @pyqtSlot()
   def UndoMove(self):
      """
      """
      try:
         self.pop()
         self.DrawBoard()
         self.ReadyForNextMove.emit(self.fen())
      except IndexError:
         pass
         
   def DrawBoard(self):
      """
         BRIEF  Redraw the chessboard based on board state
                Highlight src and dest squares for last move
                Highlight king if in check
      """
      self.svg_widget.load(self._repr_svg_().encode("utf-8"))
      
   def GetClicked(self, event):
      """
         BRIEF  Get the algebraic notation for the clicked square
      """
      top_left = self.svg_xy + self.margin
      file_i =     int((event.x() - top_left)/self.square_size)
      rank_i = 7 - int((event.y() - top_left)/self.square_size)
      return chr(file_i + 97) + str(rank_i + 1)
      
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
      
      
class PromotionDialog(QDialog):
   """
      BRIEF  A dialog used to decide what to promote a pawn to
   """
   
   def __init__(self, parent = None):
      """
         BRIF  Initialize the dialog with buttons
      """
      super().__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
      self.setWindowTitle("Promotion")
      
      radio_q = QRadioButton("q")
      radio_r = QRadioButton("r")
      radio_b = QRadioButton("b")
      radio_n = QRadioButton("n")
      
      self.button_group = QButtonGroup()
      self.button_group.addButton(radio_q)
      self.button_group.addButton(radio_r)
      self.button_group.addButton(radio_b)
      self.button_group.addButton(radio_n)
      
      radio_q.setChecked(True)
      
      radio_h_layout = QHBoxLayout()
      radio_h_layout.addWidget(radio_q)
      radio_h_layout.addWidget(radio_r)
      radio_h_layout.addWidget(radio_b)
      radio_h_layout.addWidget(radio_n)
      
      group_box = QGroupBox()
      group_box.setLayout(radio_h_layout)
      
      ok_button = QPushButton("Ok")
      cancel_button = QPushButton("Cancel")
      
      ok_button.released.connect(self.accept)
      cancel_button.released.connect(self.reject)
      
      button_h_layout = QHBoxLayout()
      button_h_layout.addWidget(ok_button)
      button_h_layout.addWidget(cancel_button)
      
      v_layout = QVBoxLayout()
      v_layout.addWidget(group_box)
      v_layout.addLayout(button_h_layout)
      self.setLayout(v_layout)
      
   def SelectedPiece(self):
      """
         BRIEF  Get the uci piece type the user selected from the dialog
      """
      return self.button_group.checkedButton().text()
      
      
class BoardControls(QWidget):
   """
      BRIEF  A UI used to modify the board
   """
   
   def __init__(self, board, parent = None):
      """
         BRIEF  Initialize the controls
      """
      super().__init__(parent)
      
      undo_button = QPushButton("Undo", self)
      
      v_layout = QVBoxLayout()
      v_layout.addWidget(undo_button)
      
      self.setLayout(v_layout)
      
      # connect signals/slots
      undo_button.released.connect(board.UndoMove)
      
      
if __name__ == "__main__":
   """
      BRIEF  Test the ChessBoard class
   """
   from PyQt5.QtWidgets import QApplication
   q_app = QApplication([])
   board = ChessBoard()
   board.UndoMove()
   board.show()
   board_controls = BoardControls(board)
   board_controls.setGeometry(300, 300, 200, 100)
   board_controls.show()
   q_app.exec()
   
   