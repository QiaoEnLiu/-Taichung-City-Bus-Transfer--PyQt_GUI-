from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

from FilePath_OOP import FilePath
from Bus_OOP import Stop, BusLine


#參考 https://github.com/QiaoEnLiu/-Taichung-City-Bus-Transfer-
#此程式碼以原始資料的顯示為主，多數串列為[{}, {}, {}, ...]
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

        self.takeBTN.clicked.connect(self.takeBus)
        # self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.toDes(stopInfo = self.table_TakeInfo, selectedBus = self.table_TakeInfo.selectedItems()))
        # self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.to_TF(stopInfo = self.table_TakeInfo, selectedBus = self.table_TakeInfo.selectedItems()))
        # self.table_To_TF_Info.itemSelectionChanged.connect(lambda:self.TF_to(stopInfo = self.table_To_TF_Info, selectedStop = self.table_To_TF_Info.selectedItems()))
        # self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes(stopInfo = self.table_TF_To_Info, selectedBus = self.table_TF_To_Info.selectedItems()))
        
        # self.table_To_TF_Info.itemSelectionChanged.connect(self.TF_to())
        # self.table_TF_To_Info.itemSelectionChanged.connect(self.toDes())
        # self.take_To_TF = self.item_to_list(self.itemAllRow(self.table_TakeInfo.selectedItems(), self.table_TakeInfo))
        # self.def_From_TF = self.item_to_list(self.itemAllRow(self.table_To_TF_Info.selectedItems(), self.table_To_TF_Info))


    #region 撘公車
    def takeBus(self):
        
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
        self.des = self.lineEdit_Des.text() #臺中車站(D月台)、逢甲大學(福星路)
        self.desInfo.busesID=Stop.IDsAtStop(self.des, self.fileList)
        self.desInfo.lineStops=Stop.busesAtStop(self.des, self.fileList)
        
        
        self.take = self.lineEdit_Take.text() #朝陽科技大學
        self.takeInfo.busesID=Stop.IDsAtStop(self.take,self.fileList)      
        self.takeInfo.lineStops=Stop.busesAtStop(self.take,self.fileList)
    
        #endregion
        
        self.table_TakeInfo.clearContents()
        self.table_To_TF_Info.clearContents()
        self.table_TF_To_Info.clearContents()
        self.tableDes.clearContents()

        self.table_TakeInfo.setRowCount(0)
        self.table_To_TF_Info.setRowCount(0)
        self.table_TF_To_Info.setRowCount(0)
        self.tableDes.setRowCount(0)

        self.tableList_Take = []
        self.tableList_To_TF = []
        self.tableList_TF_To = []

        
        #region 開始找公車撘
        #region 兩站是否在同一條路線上
        self.sameLine = Stop.sameBus(self.desInfo.busesID, self.takeInfo.busesID)
        #region 可直達
        if self.sameLine:
            #兩站有相同的公車路線，則不需要轉乘
            correctTake = []
            print("----------------不需要轉乘-----------------")
            print(f"\n從 {self.take} 撘乘：")
            for i in self.takeInfo.lineStops:
                for j in self.desInfo.lineStops:
                    if Stop.stopsVector(i,j):
                        correctTake.append(i)
                        print(f"{i[Stop.busID]}[{i[Stop.stopID]}]，",end='')
                        print(f"到 {j[Stop.stopName_CN]}[{j[Stop.stopID]}] 下車")
            self.list_to_table(self.table_TakeInfo, correctTake)
            self.table_TakeInfo.itemSelectionChanged.connect(self.toDes())

        #endregion
        
        #region 要轉乘（兩站的所有公車路線並沒有相同的公車路線）
        else:
            #兩站若沒有相同的公車路線，則需要轉乘
            print("-----------------目的地需要轉乘---------------------")

            #region 目的地站及撘乘站所有的公車路線及延站 
            self.desInfo.lines=Stop.stopInfo(self.desInfo.busesID, self.fileList)
            self.takeInfo.lines=Stop.stopInfo(self.takeInfo.busesID, self.fileList)   
            #endregion

            #region 找出行經撘乘站路線上與行經目的地站路線上相同的站點名稱
            for i in self.takeInfo.lines:
                for j in self.desInfo.lines:
                    if i[Stop.stopName_CN] == j[Stop.stopName_CN]: #為轉乘站
                        self.TF_Stops.append(i)
                        self.TF_Stops.append(j)
            self.TF_Stops = self.listToUnduplicated(self.TF_Stops)
        
            #endregion

            #region 找出從撘乘站前往轉乘站的公車
            
            for i in self.takeInfo.lines:
                for j in self.TF_Stops:
                    if Stop.stopsVector(i,j):
                        self.To_TF.append(j)
            
            self.To_TF = self.listToUnduplicated(self.To_TF)
            #endregion

            #region 撘乘站TableWeight條列出可到轉乘站的公車
            for i in self.takeInfo.lineStops:
                for j in self.To_TF:
                    if Stop.stopsVector(i,j):
                        self.tableList_Take.append(i) 

            self.tableList_Take = self.listToUnduplicated(self.tableList_Take)
            self.list_to_table(self.table_TakeInfo, self.tableList_Take)
            #endregion

            #region 找出從轉乘站前往目的地站的公車
            for i in self.TF_Stops:
                for j in self.desInfo.lines:
                    if Stop.stopsVector(i,j):
                        self.TF_To.append(i)
            self.TF_To = self.listToUnduplicated(self.TF_To)
            # self.table_TakeInfo.itemSelectionChanged.disconnect()
            # self.table_TF_To_Info.itemSelectionChanged.disconnect()
            # self.table_To_TF_Info.itemSelectionChanged.disconnect()

            # self.table_TakeInfo.blockSignals(True)
            # self.table_To_TF_Info.blockSignals(True)
            # self.table_TF_To_Info.blockSignals(True)
            self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.to_TF())
            
            # self.table_To_TF_Info.itemSelectionChanged.connect(lambda:self.TF_to())
            # self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes())
            # self.table_TakeInfo.blockSignals(False)
            # self.table_To_TF_Info.blockSignals(False)
            self.table_TF_To_Info.blockSignals(False)
            #endregion

            #region Console測試路線組合
            '''
            tempBus=""
            #region 從撘乘站
            print(f"\n從 {self.take}")
            
            #region 撘乘站
            for i in self.To_TF:
                #region 到轉乘站
                if tempBus == '' or tempBus != i[Stop.busID]:
                    tempBus=i[Stop.busID]
                    print("-------------------------\n")
                    print(f"--撘乘{i[Stop.busID]}[{i[Stop.roundTrip]}]公車")
                #endregion
            
                #region 從轉乘站
                            
                for j in self.TF_To:
                    if i[Stop.stopName_CN] == j[Stop.stopName_CN] :
                        #region 到目的地站
                        for k in self.desInfo.lineStops:
                            if Stop.stopsVector(j,k):
                                print(f"----到[{i[Stop.stopID]}] {i[Stop.stopName_CN]}",end='')
                                print(f"[{j[Stop.stopID]}] ，轉乘{j[Stop.busID]}[{j[Stop.roundTrip]}]公車，",end='')
                                print(f"抵達 {k[Stop.stopName_CN]}[{k[Stop.stopID]}]")
                        #endregion
                        
                #endregion
            #endregion
            print("-------------------------")
            '''
            #endregion
        #endregion
        #endregion
        #endregion

    #endregion

    #region 列出抵達轉乘站的公車
    def to_TF(self):
        print("To Transfer...")
        # if hasattr(self.table_To_TF_Info.itemSelectionChanged,'connect'): #lambda:self.TF_To()
        #     self.table_To_TF_Info.itemSelectionChanged.disconnect()
        # if hasattr(self.table_TF_To_Info.itemSelectionChanged,'connect'): #lambda:self.toDes()
        #     self.table_TF_To_Info.itemSelectionChanged.disconnect()
        # self.table_TakeInfo.itemSelectionChanged.disconnect()
        # self.table_TF_To_Info.itemSelectionChanged.disconnect()
        # self.table_To_TF_Info.itemSelectionChanged.disconnect()
        self.tableList_To_TF = []
        self.tableList_TF_To = []
        self.table_To_TF_Info.clearSelection()
        self.table_TF_To_Info.clearSelection()

        self.table_To_TF_Info.clearContents()
        self.table_TF_To_Info.clearContents()
        self.tableDes.clearContents()

        self.table_To_TF_Info.setRowCount(0)
        self.table_TF_To_Info.setRowCount(0)
        self.tableDes.setRowCount(0)

        self.take_To_TF = self.item_to_list(self.itemAllRow(self.table_TakeInfo.selectedItems(), self.table_TakeInfo))
        for row in self.To_TF:
            if Stop.stopsVector(self.take_To_TF[0], row):
                self.tableList_To_TF.append(row)
        self.list_to_table(self.table_To_TF_Info, self.tableList_To_TF)
        # self.table_TakeInfo.itemSelectionChanged.disconnect()
        # self.table_TF_To_Info.itemSelectionChanged.disconnect()
        # self.table_To_TF_Info.itemSelectionChanged.disconnect()
        # self.table_TakeInfo.blockSignals(True)
        # self.table_To_TF_Info.blockSignals(True)
        # self.table_TF_To_Info.blockSignals(True)
        # self.table_To_TF_Info.itemSelectionChanged.connect(lambda:self.TF_to())
        # self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes())
        # self.table_TakeInfo.blockSignals(False)
        # self.table_To_TF_Info.blockSignals(False)
        # self.table_TF_To_Info.blockSignals(False)
        # self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.to_TF())
        self.table_To_TF_Info.itemSelectionChanged.connect(lambda:self.TF_to())
        self.tableDes.blockSignals(False)
        # self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes())
    #endregion

    #region 列出由轉乘站發車的公車
    def TF_to(self):
        print("Transfer To...")
        # if hasattr(self.table_TF_To_Info.itemSelectionChanged,'connect'): #lambda:self.toDes()
        #     self.table_TF_To_Info.itemSelectionChanged.disconnect()
        self.tableList_TF_To = []
        self.table_TF_To_Info.clearSelection()

        self.table_TF_To_Info.clearContents()
        self.tableDes.clearContents()

        self.table_TF_To_Info.setRowCount(0)
        self.tableDes.setRowCount(0)
        toDesList=[]
        self.def_From_TF = self.item_to_list(self.itemAllRow(self.table_To_TF_Info.selectedItems(), self.table_To_TF_Info))
        for row in self.TF_To:
            if self.def_From_TF[0][Stop.stopName_CN] == row[Stop.stopName_CN]:
                self.tableList_TF_To.append(row)
        for take in self.tableList_TF_To:
            for stop in self.desInfo.lineStops:
                if Stop.stopsVector(take, stop):
                    toDesList.append(take)
        self.list_to_table(self.table_TF_To_Info, toDesList)
        # self.table_TakeInfo.itemSelectionChanged.disconnect()
        # self.table_TF_To_Info.itemSelectionChanged.disconnect()
        # self.table_To_TF_Info.itemSelectionChanged.disconnect()
        # self.table_TakeInfo.blockSignals(True)
        # self.table_To_TF_Info.blockSignals(True)
        # self.table_TF_To_Info.blockSignals(True)
        # self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes())
        # self.table_TakeInfo.blockSignals(False)
        # self.table_To_TF_Info.blockSignals(False)
        # self.table_TF_To_Info.blockSignals(False)
        # self.table_TakeInfo.itemSelectionChanged.connect(lambda:self.to_TF())
        # self.table_To_TF_Info.itemSelectionChanged.connect(lambda:self.TF_to())
        self.table_TF_To_Info.itemSelectionChanged.connect(lambda:self.toDes())
    #endregion

    #region 列出抵達目的地車的公車
    def toDes(self):
        print("Reach Destination.")
        self.tableDes.clearContents()
        self.tableDes.setRowCount(0)

        if self.sameLine:
            stopInfo = self.table_TakeInfo
            selectedBus = self.table_TakeInfo.selectedItems()
        else:
            stopInfo = self.table_TF_To_Info
            selectedBus = self.table_TF_To_Info.selectedItems()
         
        take = self.item_to_list(self.itemAllRow(selectedBus, stopInfo))
        self.tableDes.setRowCount(len(take))
        
        for stop in self.desInfo.lineStops:
            if Stop.stopsVector(take[0], stop):
                self.listRowToTableItem(self.tableDes, 0, stop)
    #endregion

    #region 串列元素不重覆
    #特別為原始資料的顯示，多數串列為[{}, {}, {}, ...]
    def listToUnduplicated(self, dupList):
        return list({frozenset(item.items()): item for item in dupList}.values())
    #endregion

    #region 由於QTableWidget顯示原始資料，當一列中的項目被選擇時，則輸出該列
    def itemAllRow(self, selectedBus, stopInfo):
        print(selectedBus)
        if selectedBus:
            row = selectedBus[self.headers.index(Stop.busID)].row()
            take = [stopInfo.item(row, column).text() for column in range(stopInfo.columnCount())]
            # print(take)
            return take
    #endregion


    #region 裝有字典的串列顯示到QTableWidget
    def list_to_table(self, table, list):
        table.setRowCount(len(list))
        for i, stop in enumerate(list):
            self.listRowToTableItem(table, i, stop)
    #endregion

    #region 字典每個索引對應到相同名稱的QTableWidget欄位
    def listRowToTableItem(self, table, i, stop):
        table.setItem(i, self.headers.index(Stop.busID), QTableWidgetItem(stop[Stop.busID]))
        table.setItem(i, self.headers.index(Stop.busName), QTableWidgetItem(stop[Stop.busName]))
        table.setItem(i, self.headers.index(Stop.roundTrip), QTableWidgetItem(stop[Stop.roundTrip]))
        table.setItem(i, self.headers.index(Stop.stopID), QTableWidgetItem(stop[Stop.stopID]))
        table.setItem(i, self.headers.index(Stop.stopName_CN), QTableWidgetItem(stop[Stop.stopName_CN]))
        table.setItem(i, self.headers.index(Stop.stopName_EN), QTableWidgetItem(stop[Stop.stopName_EN]))
        table.setItem(i, self.headers.index(Stop.latitude), QTableWidgetItem(stop[Stop.latitude]))
        table.setItem(i, self.headers.index(Stop.longitude), QTableWidgetItem(stop[Stop.longitude]))
    #endregion

    #region 將QTableWidget的列轉成字典並存到串列
    def item_to_list(self, data):
        # 檢查是否有資料
        if not data:
            return []

        # 創建包含字典的列表
        dict_list = [{header: value for header, value in zip(self.headers, data)}]

        return dict_list
    #endregion

    #region 列出QTableWidget所有的欄位名稱
    def get_table_headers(self, table):
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        return headers
    #endregion

    #region 將QTableWidget轉成有字典的串列
    # def tableToList(self, table):
    #     result = []
    #     for row in range(table.rowCount()):
    #         data = {
    #             Stop.busID: table.item(row, 0).text(),
    #             Stop.busName: table.item(row, 1).text(),
    #             Stop.roundTrip: table.item(row, 2).text(),
    #             Stop.stopID: table.item(row, 3).text(),
    #             Stop.stopName_CN: table.item(row, 4).text(),
    #             Stop.stopName_EN: table.item(row, 5).text(),
    #             Stop.latitude: table.item(row, 6).text(),
    #             Stop.longitude: table.item(row, 7).text(),
    #         }
    #         result.append(data)
    #     return result
    #endregion
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())