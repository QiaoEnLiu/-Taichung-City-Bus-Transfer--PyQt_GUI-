import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDesktopWidget, QDialog
from PyQt5.QtCore import pyqtSlot


import ui.takeBusMainWindows2_ui
from FilePath_OOP import FilePath
from Bus_OOP import Stop, BusLine

#此程式碼顯示處理過的資料

theStop = Stop()

pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
fileList = theStop.readFile(pathDir)

class TakeBusMainWindow(QMainWindow, ui.takeBusMainWindows2_ui.Ui_takeGUI):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.resize(800, 600)

        self.initUI()

    def initUI(self):
        self.searchButton.clicked.connect(self.searchPath)

    @pyqtSlot()
    def searchPath(self):
        #region 目的地及撘乘站
        self.desInfo=BusLine() #目的地站站點相關串列
        self.takeInfo=BusLine() #撘乘站站點相關串列
        #endregion

        #region 轉乘站
        #轉乘站站點相關串列
        self.sameLine = None #兩站是否有在相同路線上
            
        self.TF_Stops=[] #在每條路線上的轉乘站站點
        self.To_TF=[]   #可從撘乘站到轉乘站的公車
        self.TF_To=[]   #可從轉乘站到目的地站的公車
            
        #endregion

        #region 目的地站點及撘乘站點各公車及其路線延站
        self.des = self.desStopLineEdit.text()
        self.desInfo.busesID = theStop.IDsAtStop(self.des, fileList)
        self.desInfo.lineStops = theStop.busesAtStop(self.des, fileList)
        
        
        self.take = self.takeStopLineEdit.text()
        self.takeInfo.busesID = theStop.IDsAtStop(self.take, fileList)      
        self.takeInfo.lineStops = theStop.busesAtStop(self.take, fileList)
    
        #endregion

        self.sameLine = theStop.sameBus(self.desInfo.busesID, self.takeInfo.busesID)


        if self.sameLine:
            correctTake = []

            for i in self.takeInfo.lineStops:
                for j in self.desInfo.lineStops:
                    if theStop.stopsVector(i,j):
                        correctTake.append(i[theStop.busID])


            print(correctTake)

            self.takeBusList.addItems(correctTake)

        else:
            print("要轉乘")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_win = TakeBusMainWindow()
    main_win.show()
    sys.exit(app.exec_())
