from PyQt4 import QtGui, QtCore

#a widget for the items' legends
class LegendWidget(QtGui.QWidget):
    def __init__(self, parent, canvasWidget):
        super(LegendWidget, self).__init__(parent)

        self.canvasWidget = canvasWidget

        self.lineLength = 20
        self.margin = 4
        self.spacing = 4

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum))

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())

        m = max([fm.width(item.title()) for item in self.canvasWidget.attachedItems])

        # for vertical title
        return QtCore.QSize(m + 2*self.margin + self.spacing + self.lineLength, 2*self.margin + len(self.canvasWidget.attachedItems)*fm.height()*2)

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        fm = painter.fontMetrics()

        x0 = self.margin + self.lineLength + self.spacing
        y = self.margin + fm.height()
        for item in self.canvasWidget.attachedItems:
            painter.setPen(item.color())
            yl = y - fm.height()/3
            painter.drawLine(self.margin, yl, self.margin + self.lineLength, yl)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(x0, y, item.title())
            y += fm.height()*2
