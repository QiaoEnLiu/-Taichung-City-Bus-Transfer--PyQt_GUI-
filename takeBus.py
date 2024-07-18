import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDesktopWidget, QDialog
from PyQt5.QtCore import pyqtSlot

import takeBusMainWindows_ui, helloBusDailog_ui
from FilePath_OOP import FilePath
from Bus_OOP import Stop, BusLine


#參考 https://github.com/QiaoEnLiu/-Taichung-City-Bus-Transfer-
#此程式碼以原始資料的顯示為主，多數串列為[{}, {}, {}, ...]

pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
fileList = Stop.readFile(pathDir)

#region 「哈囉你好嗎？…………中興幹線」初始對話框
class HelloBusDialog(QDialog, helloBusDailog_ui.Ui_Dialog_HelloBus):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
#endregion

#region 主視窗
class TakeBusMainWindow(QMainWindow, takeBusMainWindows_ui.Ui_takeGUI):

    #region 程式讀取UI或XML的圖形介面檔（GUI）
    def __init__(self):
        super().__init__()
        # uic.loadUi("takeBus.ui", self) 
        self.setupUi(self) # 載入UI文件

        # region GUI位置
        # 取得螢幕尺寸
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 計算視窗的寬度和高度
        window_width = screen_width // 2
        window_height = screen_height
        
        # 設置視窗的大小
        self.resize(window_width, window_height)
        
        # 設置視窗的位置
        # self.move(0, 0)  # 將視窗放在螢幕的左半邊
        self.move(screen_width // 2, 0) # 視窗放在螢幕的右半邊
        #endregion

        # 初始化UI
        self.initUI()
    #endregion

    #region 其他初始化
    def initUI(self):

        self.headers = self.get_table_headers(self.table_TakeInfo)
        self.headersPath_TB = self.get_table_headers(self.table_Path)
        self.takeBTN.clicked.connect(self.takeBus)
    #endregion

    #region 撘公車
    def takeBus(self):
        print("\n-------------\n(self.takeBus)")
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

        self.takeToDesInfo=""
        self.findBus=""
        self.takeBusInfo=""
        self.startTakeInfo=""
        self.to_tf_Info=""
        self.tf_to_info=""
        self.reachInfo=""


        #region 目的地站點及撘乘站點各公車及其路線延站
        self.des = self.lineEdit_Des.text()
        self.desInfo.busesID=Stop.IDsAtStop(self.des, fileList)
        self.desInfo.lineStops=Stop.busesAtStop(self.des, fileList)
        
        
        self.take = self.lineEdit_Take.text()
        self.takeInfo.busesID=Stop.IDsAtStop(self.take, fileList)      
        self.takeInfo.lineStops=Stop.busesAtStop(self.take, fileList)

        self.findBus = f"從 {self.take} 前往 {self.des}：\n"
    
        #endregion
        
        #region 初始化
        self.cleanTable(self.table_TakeInfo)
        self.cleanTable(self.table_To_TF_Info)
        self.cleanTable(self.table_TF_To_Info)
        self.cleanTable(self.tableDes)
        self.cleanTable(self.table_Path)

        self.tableList_Take = []
        self.tableList_To_TF = []
        self.tableList_TF_To = []

        self.takeToDesInfo = ""
        self.pathPhase = "行為"
        
        #endregion


        self.table_TakeInfo.itemClicked.connect(self.to_TF)
        self.table_To_TF_Info.itemClicked.connect(self.TF_to)
        self.table_TF_To_Info.itemClicked.connect(self.toDes)
        self.tableDes.itemClicked.connect(self.reachDes)
        self.tableDes.itemClicked.connect(self.showPath)
        
        #region 開始找公車撘
        #region 兩站是否在同一條路線上
        self.sameLine = Stop.sameBus(self.desInfo.busesID, self.takeInfo.busesID)
        print(f"    (self.sameLine):{self.sameLine != None}")
        if self.sameLine:
            #region 可直達
            #兩站有相同的公車路線，則不需要轉乘
            correctTake = []
            self.takeBusInfo = "----------------不需要轉乘----------------\n"
            # print(f"從 {self.take} 撘乘：")
            # self.takeToDesInfo += "\n從 {self.take} 撘乘："
            for i in self.takeInfo.lineStops:
                for j in self.desInfo.lineStops:
                    if Stop.stopsVector(i,j):
                        correctTake.append(i)
                        # print(f"{i[Stop.busID]}[{i[Stop.stopID]}]，",end='')
                        # print(f"到 {j[Stop.stopName_CN]}[{j[Stop.stopID]}] 下車")
            self.list_to_table(self.table_TakeInfo, correctTake, isShowPath=False)
            self.table_TakeInfo.itemClicked.connect(self.toDes)

            #endregion
        
       
        else:
            #region 要轉乘
            #兩站若沒有相同的公車路線，則需要轉乘
            self.takeBusInfo = f"----------------需要轉乘----------------\n"
            #region 目的地站及撘乘站所有的公車路線及延站 
            self.desInfo.lines=Stop.stopInfo(self.desInfo.busesID, fileList)
            self.takeInfo.lines=Stop.stopInfo(self.takeInfo.busesID, fileList)   
            #endregion

            #region 找出行經撘乘站路線上與行經目的地站路線上相同的站點名稱
            for i in self.takeInfo.lines:
                for j in self.desInfo.lines:
                    if i[Stop.stopName_CN] == j[Stop.stopName_CN]: #為轉乘站

                        Stop.unduplicateList(self.To_TF, i) # 撘乘站前往轉乘站的公車
                        Stop.unduplicateList(self.TF_To, j) # 轉乘站前往目的地站的公車
                        
        
            #endregion

            #region （已停用）找出從撘乘站前往轉乘站的公車
            '''
            for i in self.takeInfo.lines:
                for j in self.TF_Stops:
                    if Stop.stopsVector(i,j):
                        self.To_TF.append(j)
            
            self.To_TF = self.listToUnduplicated(self.To_TF)
            '''
            #endregion

            #region 撘乘站TableWeight條列出可到轉乘站的公車
            for i in self.takeInfo.lineStops:
                for j in self.To_TF:
                    if Stop.stopsVector(i,j):
                        Stop.unduplicateList(self.tableList_Take, i)
            

            self.list_to_table(self.table_TakeInfo, self.tableList_Take, isShowPath=False)
            #endregion

            #region （已停用）找出從轉乘站前往目的地站的公車
            '''
            for i in self.TF_Stops:
                for j in self.desInfo.lines:
                    if Stop.stopsVector(i,j):
                        self.TF_To.append(i)
            self.TF_To = self.listToUnduplicated(self.TF_To)
            '''
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
    @pyqtSlot()
    def to_TF(self):
        print(f"\n---\n(self.to_TF)")
        
        self.tableList_To_TF = []
        self.tableList_TF_To = []
        to_TF_temp=[]

        self.cleanTable(self.table_To_TF_Info)
        self.cleanTable(self.table_TF_To_Info)
        self.cleanTable(self.tableDes)
        self.cleanTable(self.table_Path)

        selectedBus = self.table_TakeInfo.selectedItems()
        # print(f"撘乘：")
        self.take_To_TF = self.itemAllRow(selectedBus, self.table_TakeInfo)
        self.startTakeInfo = f"\n撘乘：\n{self.take_To_TF}\n"
        for row in self.To_TF:
            if Stop.stopsVector(self.take_To_TF[0], row):
                to_TF_temp.append(row)

        #region以下為避免找到只有「目的地站往轉乘站」的公車
        #   應該要找到 「撘乘站-->轉乘站 轉乘站-->目的地站」
        #   而非有 「撘乘站-->轉乘站 轉乘站<--目的地站」此結果
        for row_2TF in to_TF_temp:
            for row_TF2 in self.TF_To:
                if row_2TF[Stop.stopName_CN] == row_TF2[Stop.stopName_CN]:
                    for rowDes in self.desInfo.lineStops:
                        if Stop.stopsVector(row_TF2, rowDes):
                            Stop.unduplicateList(self.tableList_To_TF, row_2TF)
        #endregion

        self.list_to_table(self.table_To_TF_Info, self.tableList_To_TF, isShowPath=False)

    #endregion

    #region 列出由轉乘站發車的公車
    @pyqtSlot()
    def TF_to(self):
        print(f"\n---\n(self.TF_to)")

        self.tableList_TF_To = []

        self.cleanTable(self.table_TF_To_Info)
        self.cleanTable(self.tableDes)
        self.cleanTable(self.table_Path)

        toDesList=[]
        # print(f"至")
        selectedStop = self.table_To_TF_Info.selectedItems()
        self.do_TF = self.itemAllRow(selectedStop, self.table_To_TF_Info)
        self.to_tf_Info = f"\n至\n{self.do_TF}\n"
        for row in self.TF_To:
            if self.do_TF[0][Stop.stopName_CN] == row[Stop.stopName_CN]:
                self.tableList_TF_To.append(row)
        for take in self.tableList_TF_To:
            for stop in self.desInfo.lineStops:
                if Stop.stopsVector(take, stop):
                    toDesList.append(take)
        self.list_to_table(self.table_TF_To_Info, toDesList, isShowPath=False)

    #endregion

    #region 列出抵達目的地車的公車
    @pyqtSlot()
    def toDes(self):
        print(f"\n---\n(self.toDes)")

        self.cleanTable(self.tableDes)
        self.cleanTable(self.table_Path)

        self.tf_to_info = ""

        if self.sameLine:
            stopInfo = self.table_TakeInfo
            selectedBus = self.table_TakeInfo.selectedItems()
            take = self.itemAllRow(selectedBus, stopInfo)

        else:
            stopInfo = self.table_TF_To_Info
            selectedBus = self.table_TF_To_Info.selectedItems()
            # print(f"轉乘：{selectedBus}")
         
            take = self.itemAllRow(selectedBus, stopInfo)
            self.tf_to_info = f"\n轉乘：\n{take}\n"
            # print(self.tf_to_info)
        
        
        self.tf_to_des = take
        self.tableDes.setRowCount(len(take))
        
        for stop in self.desInfo.lineStops:
            if Stop.stopsVector(take[0], stop):
                self.listRowToTableItem(self.tableDes, 0, stop, isShowPath=False)
        
    #endregion

    #region 抵達目的地
    @pyqtSlot()
    def reachDes(self):
        print("\n---\n(self.reachDes)\n-------------")

        selectedStop = self.tableDes.selectedItems()
        self.arrivaDes = self.itemAllRow(selectedStop, self.tableDes)
        # print("抵達：")
        self.reachInfo = f"\n抵達：\n{self.arrivaDes}"
        self.takeToDesInfo = self.findBus + \
            self.takeBusInfo + self.startTakeInfo + \
                self.to_tf_Info + self.tf_to_info + \
                    self.reachInfo
        # self.takeToDesLabel.setText(self.takeToDesInfo)
        # print(self.takeToDesInfo)
        

    #endregion


    #region 顯示路徑
    @pyqtSlot()
    def showPath(self):
        print("\n---\n(self.showPath)\n-------------")

        self.cleanTable(self.table_Path)

        takeStr = {self.pathPhase: "撘乘"}
        to_tf_Str = {self.pathPhase: "到轉乘站"}
        tf_to_Str = {self.pathPhase: "由轉乘站"}
        desStr = {self.pathPhase: "到目的地"}

        phase=[]

        self.take_To_TF[0].update(takeStr)
        phase.append(self.take_To_TF[0])

        if self.sameLine:
            pass
        else:
            self.do_TF[0].update(to_tf_Str)
            self.tf_to_des[0].update(tf_to_Str)

            phase.append(self.do_TF[0])
            phase.append(self.tf_to_des[0])

        self.arrivaDes[0].update(desStr)
        phase.append(self.arrivaDes[0])

        self.list_to_table(self.table_Path, phase, isShowPath=True)


    #endregion

    


    #region 其他方法

    #region 取得QTableWidget所有的欄位名稱
    def get_table_headers(self, table):
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        return headers
    #endregion

    #region Table資料清除
    def cleanTable(self, table):
        table.clearContents()
        table.setRowCount(0)

    #endregion

    #region （已不使用）串列元素不重覆
    #特別為原始資料的顯示，多數串列為[{}, {}, {}, ...]
    def listToUnduplicated(self, dupList):
        return list({frozenset(item.items()): item for item in dupList}.values())
    #endregion

    #region 由於QTableWidget顯示原始資料，當一列中的項目被選擇時，則輸出該列
    def itemAllRow(self, selectedItem, table):
        if selectedItem:
            row = selectedItem[self.headers.index(Stop.busID)].row()
            rowData = [table.item(row, column).text() for column in range(table.columnCount())]
            return self.item_to_list(rowData)
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


    #region 裝有字典的串列顯示到QTableWidget
    def list_to_table(self, table, list, isShowPath):
        table.setRowCount(len(list))
        for i, stop in enumerate(list):
            self.listRowToTableItem(table, i, stop, isShowPath)
    #endregion

    #region 字典每個索引對應到相同名稱的QTableWidget欄位，並將資料加入
    def listRowToTableItem(self, table, i, stop, isShowPath):
        if isShowPath:
            headers=self.headersPath_TB
            table.setItem(i, headers.index(self.pathPhase),
                          QTableWidgetItem(stop[self.pathPhase]))
        else:
            headers=self.headers

        table.setItem(i, headers.index(Stop.busID), QTableWidgetItem(stop[Stop.busID]))
        table.setItem(i, headers.index(Stop.busName), QTableWidgetItem(stop[Stop.busName]))
        table.setItem(i, headers.index(Stop.roundTrip), QTableWidgetItem(stop[Stop.roundTrip]))
        table.setItem(i, headers.index(Stop.stopID), QTableWidgetItem(stop[Stop.stopID]))
        table.setItem(i, headers.index(Stop.stopName_CN), QTableWidgetItem(stop[Stop.stopName_CN]))
        table.setItem(i, headers.index(Stop.stopName_EN), QTableWidgetItem(stop[Stop.stopName_EN]))
        table.setItem(i, headers.index(Stop.latitude), QTableWidgetItem(stop[Stop.latitude]))
        table.setItem(i, headers.index(Stop.longitude), QTableWidgetItem(stop[Stop.longitude]))
    #endregion

    #endregion

#endregion

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    dialog_win = HelloBusDialog()

    if dialog_win.exec_() == QDialog.Accepted:
        main_win = TakeBusMainWindow()
        main_win.show()

    sys.exit(app.exec_())

