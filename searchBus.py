from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

from FilePath_OOP import FilePath
from Bus_OOP import Stop


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/searchBus.ui", self) # 載入UI文件

        # 初始化UI
        self.initUI()

    def initUI(self):

        pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
        self.fileList = Stop.readFile(pathDir)
        
        self.busID_List = []
        # self.headers = []
        # for col in range(self.busOutbound_table.columnCount()):
        #     header_item = self.busOutbound_table.horizontalHeaderItem(col).text()
        #     self.headers.append(header_item)

        self.headers = self.get_table_headers(self.busOutbound_table)
        
        tempID=''
        for row in self.fileList:
            if tempID == '' or tempID != row[Stop.busID]:
                self.busID_List.append([row[Stop.busID], row[Stop.busName]])
                tempID=row[Stop.busID]

        self.busID_table.setRowCount(len(self.busID_List))
        # 將資料加入到QTableWidget中
        for i, row in enumerate(self.busID_List):
            for j, item in enumerate(row):
                tableItem = QTableWidgetItem(str(item))  # 直接傳遞item給QTableWidgetItem的構造函數
                self.busID_table.setItem(i, j, tableItem)  # 設置QTableWidgetItem
        
        self.busID_table.itemSelectionChanged.connect(lambda:self.busInfo(selectedBus = self.busID_table.selectedItems()))
        self.searchBusInfo.clicked.connect(lambda:self.busInfo(textBus = self.lineEdit_Bus.text()))


    def busInfo(self, textBus = None, selectedBus = None):
        bus=""
        self.busOutbound_table.clearContents()
        self.busInbound_table.clearContents()

        self.busOutbound_table.setRowCount(0)
        self.busInbound_table.setRowCount(0)

        ob_list=[]
        ib_list=[]

        if textBus != None:
            selectedBus = None
            bus = textBus

        elif selectedBus != None:
            textBus = None
        
            if selectedBus:
                print(selectedBus)
                row = selectedBus[0].row()
                rowData = [self.busID_table.item(row, column).text() for column in range(self.busID_table.columnCount())]
                print(rowData)
                bus = rowData[0]

        for row in self.fileList:
            if row[Stop.busID] == bus:
                if row[Stop.roundTrip] == "去程":
                    ob_list.append(row)
                if row[Stop.roundTrip] == "回程":
                    ib_list.append(row)

        
        self.busOutbound_table.setRowCount(len(ob_list))
        self.busInbound_table.setRowCount(len(ib_list))

        if len(ob_list) == 0 and len(ib_list) == 0:
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("查無此公車：", bus)
            msg.setWindowTitle("公車查詢")
            msg.exec_()

        for i, stop in enumerate(ob_list):
            self.busOutbound_table.setItem(i, self.headers.index('站序'), QTableWidgetItem(stop['站序']))
            self.busOutbound_table.setItem(i, self.headers.index('中文站點名稱'), QTableWidgetItem(stop['中文站點名稱']))
            self.busOutbound_table.setItem(i, self.headers.index('英文站點名稱'), QTableWidgetItem(stop['英文站點名稱']))
            self.busOutbound_table.setItem(i, self.headers.index('經度'), QTableWidgetItem(stop['經度']))
            self.busOutbound_table.setItem(i, self.headers.index('緯度'), QTableWidgetItem(stop['緯度']))

        for i, stop in enumerate(ib_list):
            self.busInbound_table.setItem(i, self.headers.index('站序'), QTableWidgetItem(stop['站序']))
            self.busInbound_table.setItem(i, self.headers.index('中文站點名稱'), QTableWidgetItem(stop['中文站點名稱']))
            self.busInbound_table.setItem(i, self.headers.index('英文站點名稱'), QTableWidgetItem(stop['英文站點名稱']))
            self.busInbound_table.setItem(i, self.headers.index('經度'), QTableWidgetItem(stop['經度']))
            self.busInbound_table.setItem(i, self.headers.index('緯度'), QTableWidgetItem(stop['緯度']))

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