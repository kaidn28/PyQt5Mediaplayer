from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from FrameGrabber import *
import sys

class VideoWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "video player" 
        self.left = 500
        self.top = 300
        self.width = 800
        self.height = 600
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.playButton = QPushButton()
        self.grabPictureButton = QPushButton("Grab")
        self.positionSlider = QSlider(Qt.Horizontal)
        self.errorLabel = QLabel()
        self.frameCounter = 0
        
        #list và table, có 2 loại dùng cái nào tuỳ em 
        self.listWidget = QListWidget()
        self.tableWidget = QTableWidget(0,3) #0 là số hàng 3 là số cột  
        self.initUI()       


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #menu 
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.triggered.connect(self.openFile)
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.triggered.connect(self.exitCall)

        screenshotAction = QAction(QIcon('screenshot.png'), '&Screenshot', self)
        screenshotAction.setShortcut('Ctrl+S')
        screenshotAction.setStatusTip('Screenshot scenes')
        screenshotAction.triggered.connect(self.grab)

        fileMenu.addAction(openAction)
        fileMenu.addAction(screenshotAction)
        fileMenu.addAction(exitAction)


        # nút play, nút chụp và thanh kéo 
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.grabPictureButton.setEnabled(False)
        self.grabPictureButton.setIcon(QIcon('grabpick.png'))
        self.grabPictureButton.setToolTip('click to grab current frame')
        self.grabPictureButton.clicked.connect(self.grab)

        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        

        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)
        # Hộp điều khiển chứa nút play và slider
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.grabPictureButton)
        controlLayout.addWidget(self.positionSlider)

        # Hộp chứa video và hộp điều khiển
        
        vboxlayout = QVBoxLayout()
        vboxlayout.addWidget(self.videoWidget)
        vboxlayout.addLayout(controlLayout)
        vboxlayout.addWidget(self.errorLabel)
        
        #add vào table với list như này nhé
        x = 1
        y = 2
        t = 45
        self.listWidget.addItem('X      Y       T ')
        self.listWidget.addItem(str(x) + '      ' + str(y) + '      ' + str(t))
        self.tableWidget.insertRow(0)
        self.tableWidget.insertRow(1)
        self.tableWidget.setItem(0, 0, QTableWidgetItem("X"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("Y"))
        self.tableWidget.setItem(0,2, QTableWidgetItem("T"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem(str(x)))
        self.tableWidget.setItem(1, 1, QTableWidgetItem(str(y)))
        self.tableWidget.setItem(1,2, QTableWidgetItem(str(t)))

        layout = QGridLayout(self)
        layout.addLayout(vboxlayout, 0, 0)
        layout.addWidget(self.listWidget, 0, 1)
        layout.addWidget(self.tableWidget, 0, 2)
        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)
        
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)


        self.show()
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.grabPictureButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            self.mediaPlayer.setVideoOutput(self.videoWidget)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def grab(self):
            self.grabber = VideoFrameGrabber(self.videoWidget, self)
            self.mediaPlayer.setVideoOutput(self.grabber)
            self.grabber.frameAvailable.connect(self.process_frame)
            self.mediaPlayer.setVideoOutput(self.videoWidget)   
            self.play() 


    def process_frame(self, image):
        filename = "screenshot" + str(self.frameCounter).zfill(6)
        self.path = 'C:/Users/donam/OneDrive/Desktop/temp'
        image.save(self.path+'/{}.png'.format(str(filename)))
        self.frameCounter += 1

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())
if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    sys.exit(app.exec_())