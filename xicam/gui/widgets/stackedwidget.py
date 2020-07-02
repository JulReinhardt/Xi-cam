class StackedWidgetWithArrowButtons(QStackedWidget):
    def __init__(self, *args, **kwargs):
        QStackedWidget.__init__(self, *args, **kwargs)
        self.backwardButton = QToolButton(self)
        self.backwardButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.backwardButton.setMaximumSize(24, 24)
        self.backwardButton.setFocusPolicy(Qt.NoFocus)
        self.forwardButton = QToolButton(self)
        self.forwardButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.forwardButton.setMaximumSize(24, 24)
        self.forwardButton.setFocusPolicy(Qt.NoFocus)
        self.currentChanged.connect(self.checkSwitchButtons)

    def checkSwitchButtons(self):
        self.forwardButton.setEnabled(self.currentIndex() < self.count() - 1)
        self.backwardButton.setEnabled(self.currentIndex() > 0)

    def addWidget(self, widget):
        # this is a private method of QStackedWidget that is called when
        # the ui is being built by the program, we just implement it
        # to ensure that the buttons are correctly enabled;
        # the index *has* to be returned
        index = QStackedWidget.addWidget(self, widget)
        self.checkSwitchButtons()
        return index

    def removeWidget(self, widget):
        # not necessary, but in case you want to remove widgets in the
        # future, it will check buttons again
        index = QStackedWidget.removeWidget(self, widget)
        self.checkSwitchButtons()
        return index

    def mousePressEvent(self, event):
        # due to the way QStackedWidget is implemented, children widgets
        # that are not in its layout might not receive mouse events,
        # but we just need to track clicks so this is enough
        if event.button() == Qt.LeftButton:
            if event.pos() in self.backwardButton.geometry():
                self.setCurrentIndex(self.currentIndex() - 1)
            elif event.pos() in self.forwardButton.geometry():
                self.setCurrentIndex(self.currentIndex() + 1)

    def resizeEvent(self, event):
        # the base class resizeEvent *has* to be called, otherwise
        # you could encounter problems with children widgets
        QStackedWidget.resizeEvent(self, event)

        # now ensure that the buttons are always placed on the top
        # right corner; this positioning is completely manual and you
        # have to take button sizes in consideration to avoid
        # overlapping buttons; obviously you can place them wherever
        # you want.
        self.forwardButton.move(self.rect().right() - self.forwardButton.width(), 0)
        self.backwardButton.move(self.forwardButton.x() - self.backwardButton.width(), 0)
