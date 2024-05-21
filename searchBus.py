from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

from FilePath_OOP import FilePath
from Bus_OOP import Stop


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("searchBus.ui", self) # 載入UI文件

        # 初始化UI
        self.initUI()

    def initUI(self):

        pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
        self.fileList = Stop.readFile(pathDir)
        

        self.busID_List = []
        
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

        self.busID_table.itemSelectionChanged.connect(self.onItemSelected)

    def onItemSelected(self):
        self.busOutbound_table.clearContents()
        self.busInbound_table.clearContents()

        self.busOutbound_table.setRowCount(0)
        self.busInbound_table.setRowCount(0)

        ob_list=[]
        ib_list=[]
        

        selectedItems = self.busID_table.selectedItems()
        if selectedItems:
            row = selectedItems[0].row()
            rowData = [self.busID_table.item(row, column).text() for column in range(self.busID_table.columnCount())]
            print(rowData[0])

        for row in self.fileList:
            if row[Stop.busID] == rowData[0]:
                if row[Stop.roundTrip] == "去程":
                    ob_list.append(row)
                if row[Stop.roundTrip] == "回程":
                    ib_list.append(row)
        
        self.busOutbound_table.setRowCount(len(ob_list))
        self.busInbound_table.setRowCount(len(ib_list))
        # print(ob_list)

        for i, stop in enumerate(ob_list):
            self.busOutbound_table.setItem(i, 0, QTableWidgetItem(stop['站序']))
            self.busOutbound_table.setItem(i, 1, QTableWidgetItem(stop['中文站點名稱']))
            self.busOutbound_table.setItem(i, 2, QTableWidgetItem(stop['英文站點名稱']))
            self.busOutbound_table.setItem(i, 3, QTableWidgetItem(stop['經度']))
            self.busOutbound_table.setItem(i, 4, QTableWidgetItem(stop['緯度']))

        for i, stop in enumerate(ib_list):
            self.busInbound_table.setItem(i, 0, QTableWidgetItem(stop['站序']))
            self.busInbound_table.setItem(i, 1, QTableWidgetItem(stop['中文站點名稱']))
            self.busInbound_table.setItem(i, 2, QTableWidgetItem(stop['英文站點名稱']))
            self.busInbound_table.setItem(i, 3, QTableWidgetItem(stop['經度']))
            self.busInbound_table.setItem(i, 4, QTableWidgetItem(stop['緯度']))



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())