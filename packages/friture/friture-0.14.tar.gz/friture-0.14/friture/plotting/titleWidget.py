from PyQt4 import QtGui, QtCore

#a widget for the axis title, can be horizontal or vertical
class VerticalTitleWidget(QtGui.QWidget):
    def __init__(self, title, parent):
        super(VerticalTitleWidget, self).__init__(parent)

        self.title = title

        # for vertical title
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum))

    def setTitle(self, title):
        self.title = title

        # redraw
        self.update()

        # notify that sizeHint has changed
        self.updateGeometry()

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        # for vertical title
        return QtCore.QSize(fm.height()*1.5, fm.width(self.title))

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # for vertical title
        fm = painter.fontMetrics()
        centeredTextShift = QtCore.QPoint( -fm.width(self.title)/2, 0)

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(-90)
        painter.translate(centeredTextShift)

        painter.drawText(0, 0, self.title)


class HorizontalTitleWidget(QtGui.QWidget):
    def __init__(self, title, parent):
        super(HorizontalTitleWidget, self).__init__(parent)

        self.title = title

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed))

    def setTitle(self, title):
        self.title = title

        # redraw
        self.update()

        # notify that sizeHint has changed
        self.updateGeometry()

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        # for vertical title
        return QtCore.QSize(fm.width(self.title), fm.height()*1.5)

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        fm = painter.fontMetrics()
        centeredTextShift = QtCore.QPoint( -fm.width(self.title)/2, 0)

        painter.translate(self.width()/2, self.height()/2)
        painter.translate(centeredTextShift)

        painter.drawText(0, 0, self.title)


class ColorTitleWidget(QtGui.QWidget):
    def __init__(self, title, parent):
        super(ColorTitleWidget, self).__init__(parent)

        self.title = title

        # for vertical title
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum))

    def setTitle(self, title):
        self.title = title

        # redraw
        self.update()

        # notify that sizeHint has changed
        self.updateGeometry()

    def sizeHint(self):
        fm = QtGui.QFontMetrics(self.font())
        # for vertical title
        return QtCore.QSize(fm.height()*1.5, fm.width(self.title))

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        #painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # for vertical title
        fm = painter.fontMetrics()
        centeredTextShift = QtCore.QPoint( -fm.width(self.title)/2, 0)

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(90)
        painter.translate(centeredTextShift)

        painter.drawText(0, 0, self.title)
