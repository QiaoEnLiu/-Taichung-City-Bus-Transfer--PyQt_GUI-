import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDesktopWidget, QDialog
from PyQt5.QtCore import pyqtSlot

import ui.takeBusMainWindows_ui, ui.helloBusDailog_ui
from FilePath_OOP import FilePath
from Bus_OOP import Stop, BusLine


#參考 https://github.com/QiaoEnLiu/-Taichung-City-Bus-Transfer-
#此程式碼以原始資料的顯示為主，多數串列為[{}, {}, {}, ...]

theStop = Stop()

pathDir = FilePath("臺中市市區公車站牌資料", "CSV").path()
fileList = theStop.readFile(pathDir)

#region 「哈囉你好嗎？…………中興幹線」初始對話框
class HelloBusDialog(QDialog, ui.helloBusDailog_ui.Ui_Dialog_HelloBus):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
#endregion

#region 主視窗
class TakeBusMainWindow(QMainWindow, ui.takeBusMainWindows_ui.Ui_takeGUI):

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


        #region 連接事件
        """
        如果元件未在初始化中連接事件，會在後續元件反覆觸發事件中，之前的事件也會被保留並一同執行；
        所以元件為確保只有一次的事件，需在初始化中連接事件，並撘配@pyqtSlot()進一步改善效能；
        但撘乘公車後，因後續有「直達」及「轉乘」兩種條件而有兩種事件，且以同一元件使用，為避免反覆執行時造成先前的事件保留，
        則預設事件為無，然後再選擇「直達」或「轉乘」之前，先將之前的連接解除；
        """
        self.takeBTN.clicked.connect(self.takeBus) # 只有一種事件
        self.table_TakeInfo.itemClicked.connect() # 有「直達」及「轉乘」兩種條件
        self.table_To_TF_Info.itemClicked.connect(self.TF_to) # 只有一種事件
        self.table_TF_To_Info.itemClicked.connect(self.toDes) # 只有一種事件
        self.tableDes.itemClicked.connect(self.reachDes) # 只有一種事件

        #endregion

        
    #endregion


    #region 撘公車
    @pyqtSlot()
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
        self.desInfo.busesID = theStop.IDsAtStop(self.des, fileList)
        self.desInfo.lineStops = theStop.busesAtStop(self.des, fileList)
        
        
        self.take = self.lineEdit_Take.text()
        self.takeInfo.busesID = theStop.IDsAtStop(self.take, fileList)      
        self.takeInfo.lineStops = theStop.busesAtStop(self.take, fileList)

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

        
        #region 開始找公車撘
        self.table_TakeInfo.itemClicked.disconnect() # 解除之前的事件
        #region 兩站是否在同一條路線上
        self.sameLine = theStop.sameBus(self.desInfo.busesID, self.takeInfo.busesID)
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
                    if theStop.stopsVector(i,j):
                        correctTake.append(i)
                        # print(f"{i[theStop.busID]}[{i[theStop.stopID]}]，",end='')
                        # print(f"到 {j[theStop.stopName_CN]}[{j[theStop.stopID]}] 下車")
            self.list_to_table(self.table_TakeInfo, correctTake, isShowPath=False)
            self.table_TakeInfo.itemClicked.connect(self.toDes) # 「直達」事件
            #endregion
        
       
        else:
            #region 要轉乘
            #兩站若沒有相同的公車路線，則需要轉乘
            self.takeBusInfo = f"----------------需要轉乘----------------\n"
            #region 目的地站及撘乘站所有的公車路線及延站 
            self.desInfo.lines = theStop.stopInfo(self.desInfo.busesID, fileList)
            self.takeInfo.lines = theStop.stopInfo(self.takeInfo.busesID, fileList)   
            #endregion

            #region 找出行經撘乘站路線上與行經目的地站路線上相同的站點名稱
            for i in self.takeInfo.lines:
                for j in self.desInfo.lines:
                    if i[theStop.stopName_CN] == j[theStop.stopName_CN]: #為轉乘站

                        theStop.unduplicateList(self.To_TF, i) # 撘乘站前往轉乘站的公車
                        theStop.unduplicateList(self.TF_To, j) # 轉乘站前往目的地站的公車
                        
            #endregion

            #region 撘乘站TableWeight條列出可到轉乘站的公車
            for i in self.takeInfo.lineStops:
                for j in self.To_TF:
                    if theStop.stopsVector(i,j):
                        theStop.unduplicateList(self.tableList_Take, i)
            

            self.list_to_table(self.table_TakeInfo, self.tableList_Take, isShowPath=False)
            #endregion
            self.table_TakeInfo.itemClicked.connect(self.to_TF)  #「轉乘」事件（前往轉乘站）
        

            #region Console測試路線組合
            
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
            if theStop.stopsVector(self.take_To_TF[0], row):
                to_TF_temp.append(row)

        #region以下為避免找到只有「目的地站往轉乘站」的公車
        #   應該要找到 「撘乘站-->轉乘站 轉乘站-->目的地站」
        #   而非有 「撘乘站-->轉乘站 轉乘站<--目的地站」此結果

        for row_2TF in to_TF_temp: # 到轉乘站的公車
            for row_TF2 in self.TF_To: # 到目的地站的轉乘站的公車
                if row_2TF[theStop.stopName_CN] == row_TF2[theStop.stopName_CN]: # 換乘（同一站換撘）
                    for rowDes in self.desInfo.lineStops: # 到目的地站的公車
                        if theStop.stopsVector(row_TF2, rowDes): # 由轉乘站到目的地站
                            theStop.unduplicateList(self.tableList_To_TF, row_2TF) 
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
            if self.do_TF[0][theStop.stopName_CN] == row[theStop.stopName_CN]:
                self.tableList_TF_To.append(row)
        for take in self.tableList_TF_To:
            for stop in self.desInfo.lineStops:
                if theStop.stopsVector(take, stop):
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
            # 可直達
            stopInfo = self.table_TakeInfo
            selectedBus = self.table_TakeInfo.selectedItems()
            take = self.itemAllRow(selectedBus, stopInfo)
            self.takeToDes = take

        else:
            # 要轉乘
            stopInfo = self.table_TF_To_Info
            selectedBus = self.table_TF_To_Info.selectedItems()
            # print(f"轉乘：{selectedBus}")
         
            take = self.itemAllRow(selectedBus, stopInfo)
            self.tf_to_info = f"\n轉乘：\n{take}\n"
            # print(self.tf_to_info)
            self.tf_to_des = take

        self.tableDes.setRowCount(len(take))
        
        for stop in self.desInfo.lineStops:
            if theStop.stopsVector(take[0], stop):
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
        self.showPath()
        

    #endregion


    #region 顯示路徑
    # @pyqtSlot()
    def showPath(self):
        print("\n---\n(self.showPath)\n-------------")

        self.cleanTable(self.table_Path)
        # self.table_Path與其他table不同多了一「行為」欄
        takeStr = {self.pathPhase: "撘乘"}
        to_tf_Str = {self.pathPhase: "到轉乘站"}
        tf_to_Str = {self.pathPhase: "由轉乘站"}
        desStr = {self.pathPhase: "到目的地"}

        phase=[]


        if self.sameLine:
            # 直達
            self.takeToDes[0].update(takeStr)
            phase.append(self.takeToDes[0])
        else:
            # 轉乘
            self.take_To_TF[0].update(takeStr)
            self.do_TF[0].update(to_tf_Str)
            self.tf_to_des[0].update(tf_to_Str)

            phase.append(self.take_To_TF[0])
            phase.append(self.do_TF[0])
            phase.append(self.tf_to_des[0])

        self.arrivaDes[0].update(desStr)
        phase.append(self.arrivaDes[0])

        self.list_to_table(self.table_Path, phase, isShowPath=True)


    #endregion

    
    #region 其他針對QTableWidget方法

    #region 取得QTableWidget所有的欄位名稱
    def get_table_headers(self, table):
        headers = []
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                headers.append(header_item.text())
        return headers
    #endregion


    #region QTableWidget資料清除
    def cleanTable(self, table):
        table.clearContents()
        table.setRowCount(0)

    #endregion

    #region 由於QTableWidget顯示原始資料，當一列中的項目被選擇時，則輸出該列
    def itemAllRow(self, selectedItem, table):
        if selectedItem:
            row = selectedItem[self.headers.index(theStop.busID)].row()
            rowData = [table.item(row, column).text() for column in range(table.columnCount())]
            return self.item_to_list(rowData)
    #endregion

    #region 將QTableWidget的列轉成字典並存到串列
    # #特別為原始資料的顯示，多數串列結構為[{}, {}, {}, ...]
    def item_to_list(self, data):
        # 檢查是否有資料
        if not data:
            return []

        # 創建包含字典的串列
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
            # self.table_Path與其他table不同多了一「行為」欄
            headers=self.headersPath_TB
            table.setItem(i, headers.index(self.pathPhase),
                          QTableWidgetItem(stop[self.pathPhase]))
        else:
            headers=self.headers

        table.setItem(i, headers.index(theStop.busID), QTableWidgetItem(stop[theStop.busID]))
        table.setItem(i, headers.index(theStop.busName), QTableWidgetItem(stop[theStop.busName]))
        table.setItem(i, headers.index(theStop.roundTrip), QTableWidgetItem(stop[theStop.roundTrip]))
        table.setItem(i, headers.index(theStop.stopID), QTableWidgetItem(stop[theStop.stopID]))
        table.setItem(i, headers.index(theStop.stopName_CN), QTableWidgetItem(stop[theStop.stopName_CN]))
        table.setItem(i, headers.index(theStop.stopName_EN), QTableWidgetItem(stop[theStop.stopName_EN]))
        table.setItem(i, headers.index(theStop.latitude), QTableWidgetItem(stop[theStop.latitude]))
        table.setItem(i, headers.index(theStop.longitude), QTableWidgetItem(stop[theStop.longitude]))
    #endregion

    #endregion

    #region （已不使用）串列元素不重覆
    #特別為原始資料的顯示，多數串列為[{}, {}, {}, ...]
    def listToUnduplicated(self, dupList):
        return list({frozenset(item.items()): item for item in dupList}.values())
    #endregion

#endregion

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    dialog_win = HelloBusDialog()

    if dialog_win.exec_() == QDialog.Accepted:
        main_win = TakeBusMainWindow()
        main_win.show()

    sys.exit(app.exec_())

