from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

from FilePath_OOP import FilePath
from Bus_OOP import Stop

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("takeBus.ui", self) # 載入UI文件

        # 初始化UI
        self.initUI()

    def initUI(self):
        pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
        self.fileList = Stop.readFile(pathDir)

        self.headers = self.get_table_headers(self.table_TakeInfo)

        self.takeBTN.clicked.connect(self.take)



    def take(self):

        self.table_TakeInfo.clearContents()
        self.table_To_TF_Info.clearContents()
        self.table_TF_To_Info.clearContents()
        self.tableDes.clearContents()

        self.table_TakeInfo.setRowCount(0)
        self.table_To_TF_Info.setRowCount(0)
        self.table_TF_To_Info.setRowCount(0)
        self.tableDes.setRowCount(0)

        #region 目的地站點及撘乘站點各公車及其路線延站
        self.des = self.lineEdit_Des.text()
        self.desBus=Stop.IDsAtStop(self.des, self.fileList)
        self.desStop=Stop.busesAtStop(self.des, self.fileList)
        
        
        self.take = self.lineEdit_Take.text()
        self.takeBus=Stop.IDsAtStop(self.take,self.fileList)      
        self.takeStop=Stop.busesAtStop(self.take,self.fileList)
    
        #endregion

        self.table_TakeInfo.setRowCount(len(self.takeStop))
        for i, stop in enumerate(self.takeStop):
            
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.busID), QTableWidgetItem(stop[Stop.busID]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.busName), QTableWidgetItem(stop[Stop.busName]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.roundTrip), QTableWidgetItem(stop[Stop.roundTrip]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.stopID), QTableWidgetItem(stop[Stop.stopID]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.stopName_CN), QTableWidgetItem(stop[Stop.stopName_CN]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.stopName_EN), QTableWidgetItem(stop[Stop.stopName_EN]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.latitude), QTableWidgetItem(stop[Stop.latitude]))
                self.table_TakeInfo.setItem(i, self.headers.index(Stop.longitude), QTableWidgetItem(stop[Stop.longitude]))
            
        #region 開始找公車撘
        #region 可直達（兩站在同一條路線上）
        if Stop.sameBus(self.desBus, self.takeBus):
            #兩站有相同的公車路線，則不需要轉乘
            
            print("----------------不需要轉乘-----------------")
            # takeInfoList = self.table_to_list(self.table_TakeInfo)
            self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.toDes(takeInfo = self.table_TakeInfo, selectedBus = self.table_TakeInfo.selectedItems()))


            
            print(f"\n從 {self.take} 撘乘：")
            for i in self.takeStop:
                for j in self.desStop:
                    if Stop.stopsVector(i,j):
                        print(f"{i[Stop.busID]}[{i[Stop.stopID]}]，",end='')
                        print(f"到 {j[Stop.stopName_CN]}[{j[Stop.stopID]}] 下車")

        #endregion
        
        #region 要轉乘（兩站的所有公車路線並沒有相同的公車路線）
        else:
            #兩站若沒有相同的公車路線，則需要轉乘
            print("-----------------目的地需要轉乘---------------------")
        #endregion
        #endregion

    def to_TF(self, selectedBus = None):
        pass

    def TF_to(self, selectedStop = None):
        pass

    def toDes(self, takeInfo = None, selectedBus = None):
        self.tableDes.clearContents()
        self.tableDes.setRowCount(0)
        if selectedBus:
            row = selectedBus[self.headers.index(Stop.busID)].row()
            take = [takeInfo.item(row, column).text() for column in range(takeInfo.columnCount())]
        take = self.item_to_list(take)
        self.tableDes.setRowCount(len(take))
        print(take)
        print(len(self.desStop))
        for stop in self.desStop:
            if Stop.stopsVector(take[0], stop):
                
                self.tableDes.setItem(0, self.headers.index(Stop.busID), QTableWidgetItem(stop[Stop.busID]))
                self.tableDes.setItem(0, self.headers.index(Stop.busName), QTableWidgetItem(stop[Stop.busName]))
                self.tableDes.setItem(0, self.headers.index(Stop.roundTrip), QTableWidgetItem(stop[Stop.roundTrip]))
                self.tableDes.setItem(0, self.headers.index(Stop.stopID), QTableWidgetItem(stop[Stop.stopID]))
                self.tableDes.setItem(0, self.headers.index(Stop.stopName_CN), QTableWidgetItem(stop[Stop.stopName_CN]))
                self.tableDes.setItem(0, self.headers.index(Stop.stopName_EN), QTableWidgetItem(stop[Stop.stopName_EN]))
                self.tableDes.setItem(0, self.headers.index(Stop.latitude), QTableWidgetItem(stop[Stop.latitude]))
                self.tableDes.setItem(0, self.headers.index(Stop.longitude), QTableWidgetItem(stop[Stop.longitude]))

            
        

    
    # def table_to_list(self, table):
    #     cols = table.columnCount()
    #     rows = table.rowCount()
    #     # headers = [table.horizontalHeaderItem(col).text() for col in range(cols)]
    #     table_list = []

    #     for row in range(rows):
    #         row_data = {}
    #         for col in range(cols):
    #             item = table.item(row, col)
    #             row_data[self.headers[col]] = item.text() if item else ""
    #         table_list.append(row_data)

    #     print(table_list)

    #     return table_list
    

    def item_to_list(self, data):
        # 檢查是否有資料
        if not data:
            return []

        # 創建包含字典的列表
        dict_list = [{header: value for header, value in zip(self.headers, data)}]

        return dict_list
    
    def get_table_headers(self, table):
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        return headers
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())