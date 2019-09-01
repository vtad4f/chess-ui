#
# MERGED TWO SOLUTIONS FROM:
#    https://stackoverflow.com/questions/47287328/get-clicked-chess-piece-from-an-svg-chessboard
#

import chess
import chess.svg
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget


class MainWindow(QWidget):
    """
    Create a surface for the chessboard.
    """
    
    def __init__(self):
        """
        Initialize the chessboard.
        """
        super().__init__()

        self.setWindowTitle("Chess Titan")
        self.setGeometry(300, 300, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.svgX = 50                          # top left x-pos of chessboard
        self.svgY = 50                          # top left y-pos of chessboard
        self.cbSize = 600                       # size of chessboard
        self.widgetSvg.setGeometry(self.svgX,self.svgY, self.cbSize, self.cbSize)
        self.coordinates = True
        # see chess.svg.py line 129
        self.margin = 0.05*self.cbSize if self.coordinates == True else 0
        self.squareSize  = (self.cbSize - 2 * self.margin) / 8.0
        self.chessboard = chess.Board()
        self.pieceToMove = [None, None]
        self.drawBoard()
        
    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        """
        Handle left mouse clicks and enable moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        if event.x()
        if self.svgX < event.x() <= self.svgX + self.cbSize and self.svgY < event.y() <= self.svgY + self.cbSize:   # mouse on chessboard
            if event.buttons() == Qt.LeftButton:
                # if the click is on chessBoard only
                if self.svgX + self.margin < event.x() < self.svgX + self.cbSize - self.margin and self.svgY + self.margin < event.y() < self.svgY + self.cbSize - self.margin:
                    file = int((event.x() - (self.svgX + self.margin))/self.squareSize)             
                    rank = 7 - int((event.y() - (self.svgY + self.margin))/self.squareSize) 
                    square = chess.square(file, rank)                       # chess.sqare.mirror() if white is on top
                    piece = self.chessboard.piece_at(square)
                    coordinates = '{}{}'.format(chr(file + 97), str(rank +1))
                    if self.pieceToMove[0] is not None:
                        move = chess.Move.from_uci('{}{}'.format(self.pieceToMove[1], coordinates))
                        if move in self.chessboard.legal_moves:
                            self.chessboard.push(move)
                            print(self.chessboard.fen())
                        piece = None
                        coordinates= None
                    self.pieceToMove = [piece, coordinates]
                    self.drawBoard()

    def drawBoard(self):
        """
        Draw a chessboard with the starting position and then redraw
        it for every new move.
        """
        self.chessboardSvg = self.chessboard._repr_svg_().encode("UTF-8")
        self.drawBoardSvg = self.widgetSvg.load(self.chessboardSvg)

if __name__ == "__main__":
    chessTitan = QApplication([])
    window = MainWindow()
    window.show()
    chessTitan.exec()
    
    