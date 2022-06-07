#                 PyQt5 Custom Widgets                #
#                GPL 3.0 - Kadir Aksoy                #
#   https://github.com/kadir014/pyqt5-custom-widgets  #
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, pyqtProperty, pyqtSlot, Q_ENUMS
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
try:
    from animation import Animation, AnimationHandler
except ModuleNotFoundError:
    from .animation import Animation, AnimationHandler
from enum import Enum
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)


class StylesEnum:
    win10 = 0
    ios = 1
    android = 2


class ToggleSwitch(QWidget):

    class GeneralEnum:
        __reference_class = StylesEnum

        def __new__(cls, key_int):
            for key, val in filter(lambda item: not item[0].startswith('_'), cls.__dict__.items()):
                reference_val = getattr(cls.__reference_class, key)
                if reference_val is not None and reference_val == key_int:
                    return val
            else:
                raise Exception(f'the key {key_int} has not been found in {cls.__class__}')

    class OnColorEnum(GeneralEnum):
        win10 = QColor(0, 116, 208)
        ios = QColor(73, 208, 96)
        android = QColor(0, 150, 136)

    class OffColorEnum(GeneralEnum):
        win10 = QColor(0, 0, 0)
        ios = QColor(250, 250, 250)
        android = QColor(255, 255, 255)

    class HandleColorEnum(GeneralEnum):
        win10 = QColor(255, 255, 255)
        ios = QColor(255, 255, 255)
        android = QColor(255, 255, 255)

    Q_ENUMS(StylesEnum)
    defaultStyles = (StylesEnum.win10, StylesEnum.ios, StylesEnum.android)

    toggled = pyqtSignal()
    styleChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._text = ''
        self._on = False
        # TODO: find a better way for opacity
        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(1)
        self.setGraphicsEffect(self.opacity)
        self._style = None
        self._default_style = StylesEnum.ios #self.StylesEnum.win10
        self.styleChanged.connect(self._apply_style)
        self._style = self.reset_style()
        self.anim = AnimationHandler(self, 0, self.width, Animation.easeOutCirc)
        if self._on: self.anim.value = 1

    @property
    def default_style(self):
        return self._default_style

    @default_style.setter
    def default_style(self, style):
        return

    # @property
    # def onColor(self):
    #     return self._onColor
    #
    # #onColor.setter
    # def onColor(self, color_enum):
    #     ...

    @pyqtSlot(int)
    def _apply_style(self, style):
        if style  == StylesEnum.win10:
            self.onColor  = self.OnColorEnum(StylesEnum.win10)
            self.offColor = QColor(0, 0, 0)

            self.handleAlpha = True
            self.handleColor = QColor(255, 255, 255)

            self.width = 35
            self.radius = 26

        elif style  == StylesEnum.ios:
            self.onColor  = QColor(73, 208, 96)
            self.offColor = QColor(250, 250, 250)

            self.handleAlpha = False
            self.handleColor = QColor(255, 255, 255)

            self.width = 21
            self.radius = 29

        elif style  == StylesEnum.android:
            self.onColor  = QColor(0, 150, 136)
            self.offColor = QColor(255, 255, 255)

            self.handleAlpha = True
            self.handleColor = QColor(255, 255, 255)

            self.width = 35
            self.radius = 26
        self.setMinimumSize(self.width + (self.radius * 2) + (len(self._text) * 10), self.radius + 2)
        super(ToggleSwitch, self).update()


    def get_style(self):
        return self._style

    @pyqtSlot(str)
    def set_style(self, style:StylesEnum):
        if style == self._style:
            return
        if style not in ToggleSwitch.defaultStyles:
            raise Exception(f"'{style}' is not a default style.")
        self._style = style
        self.styleChanged.emit(style)

    def reset_style(self):
        self.set_style(self.default_style)
        return self.default_style


    # @pyqtSlot(str)
    # def set_style(self, style):
    #     self._style = style
    #


    style = pyqtProperty(StylesEnum, get_style, set_style, reset_style)


    def __repr__(self):
        return f"<pyqt5Custom.ToggleSwitch(isToggled={self.isToggled()})>"

    def isToggled(self):
        return self._on

    def desaturate(self, color):
        cc = getattr(self, color)
        h = cc.hue()
        if h < 0: h = 0
        s = cc.saturation()//4
        if s > 255: s = 255
        c = QColor.fromHsv(h, s, cc.value())
        setattr(self, color, c)

    def saturate(self, color):
        cc = getattr(self, color)
        h = cc.hue()
        if h < 0: h = 0
        s = cc.saturation()*4
        if s > 255: s = 255
        c = QColor.fromHsv(h, s, cc.value())
        setattr(self, color, c)

    def update(self, *args, **kwargs):
        self.anim.update()
        super().update(*args, **kwargs)

    def mousePressEvent(self, event):
        if self.isEnabled():
            if self._on:
                self._on = False
                self.anim.start(reverse=True)
            else:
                self._on = True
                self.anim.start()
            self.update()

            self.toggled.emit()

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            if self.isEnabled():
                self.saturate("onColor")
                self.saturate("offColor")
                self.saturate("handleColor")
                self.opacity.setOpacity(1.00)
            else:
                self.desaturate("onColor")
                self.desaturate("offColor")
                self.desaturate("handleColor")
                self.opacity.setOpacity(0.4)

            self.update()

        else:
            super().changeEvent(event)

    def paintEvent(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.Antialiasing)

        if self._style  == StylesEnum.win10:

            if self._on:
                pen = QPen(self.onColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)
                brush = QBrush(self.onColor)
                pt.setBrush(brush)


                r = self.radius
                w = self.width

                pt.drawChord(r, 1, r, r, 90*16, 180*16)
                pt.drawChord(r+w, 1, r, r, -90*16, 180*16)
                pt.drawRect(r+r//2, 1, w, r)

                if self.handleAlpha: pt.setBrush(pt.background())
                else: pt.setBrush(QBrush(self.handleColor))
                offset = r*0.4
                pt.drawEllipse(r+offset/2+self.anim.current() , 1+offset/2 , r-offset , r-offset)

            else:
                pen = QPen(self.offColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)

                r = self.radius
                w = self.width

                pt.drawArc(r, 1, r, r, 90*16, 180*16)
                pt.drawArc(r+w, 1, r, r, -90*16, 180*16)
                pt.drawLine(r+r//2, 1, r+w+r//2, 1)
                pt.drawLine(r+r//2, r+1, r+w+r//2, r+1)

                brush = QBrush(self.offColor)
                pt.setBrush(brush)
                offset = r*0.4
                pt.drawEllipse(r+offset/2+self.anim.current() , offset/2+1 , r-offset , r-offset)

        elif self._style  == StylesEnum.ios:

            if self._on:
                pen = QPen(self.onColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)
                brush = QBrush(self.onColor)
                pt.setBrush(brush)

                r = self.radius
                w = self.width

                pt.drawChord(r, 1, r, r, 90*16, 180*16)
                pt.drawChord(r+w, 1, r, r, -90*16, 180*16)
                pt.drawRect(r+r//2, 1, w, r)

                if self.handleAlpha: pt.setBrush(pt.background())
                else: pt.setBrush(QBrush(self.handleColor))
                offset = r*0.025
                pt.drawEllipse(r+offset/2+self.anim.current() , 1+offset/2 , r-offset , r-offset)

            else:
                pen = QPen(self.offColor.darker(135), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)
                brush = QBrush(self.offColor)
                pt.setBrush(brush)

                r = self.radius
                w = self.width

                pt.drawChord(r, 1, r, r, 90*16, 180*16)
                pt.drawChord(r+w, 1, r, r, -90*16, 180*16)
                pt.drawRect(r+r//2, 1, w, r)
                pt.setPen(QPen(self.offColor))
                pt.drawRect(r+r//2-2, 2, w+4, r-2)

                if self.handleAlpha: pt.setBrush(pt.background())
                else: pt.setBrush(QBrush(self.handleColor))
                pt.setPen(QPen(self.handleColor.darker(160)))
                offset = r*0.025
                pt.drawEllipse(r+offset/2+self.anim.current() , 1+offset/2 , r-offset , r-offset)

        elif self._style  == StylesEnum.android:

            if self._on:
                pen = QPen(self.onColor.lighter(145), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)
                brush = QBrush(self.onColor.lighter(145))
                pt.setBrush(brush)

                r = self.radius
                w = self.width

                pt.drawChord(r+r//4, 1+r//4, r//2, r//2, 90*16, 180*16)
                pt.drawChord(r+w+r//4, 1+r//4, r//2, r//2, -90*16, 180*16)
                pt.drawRect(r+r//2, 1+r//4, w, r//2)

                pt.setBrush(QBrush(self.onColor))
                pt.setPen(QPen(self.onColor))
                pt.drawEllipse(r+self.anim.current(), 1 , r, r)

            else:
                pen = QPen(self.offColor.darker(130), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                pt.setPen(pen)
                brush = QBrush(self.offColor.darker(130))
                pt.setBrush(brush)

                r = self.radius
                w = self.width

                pt.drawChord(r+r//4, 1+r//4, r//2, r//2, 90*16, 180*16)
                pt.drawChord(r+w+r//4, 1+r//4, r//2, r//2, -90*16, 180*16)
                pt.drawRect(r+r//2, 1+r//4, w, r//2)

                pt.setBrush(QBrush(self.offColor))
                pt.setPen(QPen(self.offColor.darker(140)))
                pt.drawEllipse(r+self.anim.current(), 1 , r, r)

        font = pt.font()
        pt.setFont(font)
        pt.setPen(QPen(Qt.black))

        pt.drawText(w+r*2+10, r//2+r//4, self._text)

        pt.end()

        if not self.anim.done(): self.update()

