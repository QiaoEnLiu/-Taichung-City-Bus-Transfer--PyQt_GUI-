# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 12:24:44 2023

@author: User
"""
import csv
import pandas as pd

#region 公車路線變數
class BusLine:
    
    def __init__(self):
        
        self.busesID=[] #行經該站點的公車編號
        self.lines=[] #行經該站點公車路線
        self.lineStops=[] #在每條路線上的該站點

#endregion

#region 與站點互動功能
class Stop:
    
    #Resource/臺中市市區公車站牌資料.CSV    
    
    #region

    '''
    def __init__(self,busID,busName,roundTrip,stopID,stopName_CN,stopName_EN,latitude,longitude): #針對公車CSV檔欄位所呈現的物件Bus，但目前用不到
                
        self.busID=busID #路線：路線編號
        self.busName=busName #路線名稱：名稱為「端點A站 - 端點B站」
        self.roundTrip=roundTrip #方向：路線名稱「端點A站 - 端點B站」為去程(outbound)，「端點A站」為發車站，站序1；而回程(inbound)以「端點B站」發車，「端點B站」站序為1，為回程發車站
        self.stop=stopID #站序：發車站點（端點）為1，數字遞增為行車方向，也可稱「向量」
        self.stopName_CN=stopName_CN #中文站點名稱
        self.stopName_EN=stopName_EN #English Stop Name
        self.latitude=latitude #經度
        self.longitude=longitude #緯度
        
        '''
    #endregion

    #region 欄位名稱
    def __init__(self):
        self.busID='路線' #路線：路線編號 / Stop.busID
        self.busName='路線名稱' #路線名稱：名稱為「端點A站 - 端點B站」 / Stop.busName
        self.roundTrip='方向' #方向 / Stop.roundTrip
        self.stopID='站序' #站序：發車站點（端點）為1，數字遞增為行車方向，也可稱「向量」 / Stop.stopID
        self.stopName_CN='中文站點名稱' #中文站點名稱 / Stop.stopName_CN
        self.stopName_EN='英文站點名稱' #English Stop Name / Stop.stopName_EN
        self.latitude='經度' #經度 / Stop.latitude
        self.longitude='緯度' #緯度 / Stop.longitude
        
        #路線方向分為兩種
        self.roundTrip_ob='去程' #路線名稱「端點A站 - 端點B站」為去程(outbound)，「端點A站」為發車站 / Stop.roundTrip_ob
        self.roundTrip_ib='回程' #回程(inbound)以「端點B站」發車 / Stop.roundTrip_ib
    #endregion

    
    #region 讀取url「臺中市市區公車站牌資料」url
    def readOnlineFile(self):
        
        url='https://datacenter.taichung.gov.tw/swagger/OpenData/2dd516a9-510f-424e-91d8-17dae9cedf99'
        df=pd.read_csv(url,encoding='big5')
        #return df.to_dict('records')
        return df
        
        
    #endregion

    #region 讀CSV檔
    def readFile(self, filePath):
        
        busList=[]             
        with open(filePath,newline='',encoding='utf-8-sig') as csvFile:   #encoding='utf-8-sig'     
            rows=csv.DictReader(csvFile)
            for row in rows:
                busList.append(row)                       
        csvFile.close()
        return busList
    
    #endregion

    #region 查行經該站點所有的公車編號
    def IDsAtStop(self, stop, busList):
       
        busIDList=[]
        #region 迴圈記憶法
        '''
        temp=''
        for i in busList:
            if stop in i[self.stopName_CN]:
                if temp == '' or temp != i[self.busID]:  
                    busIDList.append(i[self.busID])
                    temp=i[self.busID]
        '''
        #endregion
        
        for i in busList:
            if stop in i[self.stopName_CN]:
                self.unduplicateList(busIDList, i[self.busID])
        
        return busIDList

    #endregion

    #region 查行經該站點的路線編號（輸出該站點行）
    def busesAtStop(self, takeStop, busList): 
    
        busIDList=[]
        for i in busList:
            if takeStop in i[self.stopName_CN]:
                busIDList.append(i)
        return busIDList
    
    #endregion

    #region 是否有公車可直達
    def sameBus(self, desBus, takeBus): 
        #轉乘程式碼中，判斷是否需要轉乘
            
        for i in desBus:
            for j in takeBus:
                if i == j:
                    return i == j
    #endregion
   
    
    #region 站牌路線資訊                                
    def stopInfo(self, busesID, busList):
        #列出行經該站的公車路線，要先由IDsAtStop函式前找出行經該站的路線編號，再透過路線編號從已讀取的資料集串列，找出每條路線上的每個站點
        #如同在公車站上看到的公車站牌
            
        busLine=[]
        for i in busesID:
            tempList=[] 
            for j in busList:
                if i == j[self.busID]:        
                    tempList.append(j)
            busLine.extend(tempList)
            
        return busLine
    #endregion

    #region 路線延站
    def linesAtStop(self, busID, tempList, busList): 
        #從站牌上的公車路線延站
        
        for i in busList:
            if busID == i[self.busID]:        
                tempList.append(i)
        
    #endregion

    #region 兩條硌線相同站點
    def sameStops(self, bus1, bus2, busList):
        
        bus1Stops=[]
        bus2Stops=[]
        sameStops=[]        
        self.linesAtStop(bus1,bus1Stops,busList)
        self.linesAtStop(bus2,bus2Stops,busList)        
        for i in bus1Stops:
            for j in bus2Stops:
                if i[self.stopName_CN] == j[self.stopName_CN]:
                    sameStops.append(i)
                    sameStops.append(j)
                    break
                
        return sameStops
    #endregion

    #region #撘乘站與目的地站相關性
    def stopsVector(self, take, des):
        
        sameBus = take[self.busID] == des[self.busID] # 是否在同一條路線
        sameDirection = take[self.roundTrip] == des[self.roundTrip] # 是否同個方向
        takeToDes = int(take[self.stopID]) < int(des[self.stopID]) # 是否目的地站在撘乘站之後（行經順序）
    
        return sameBus and sameDirection and takeToDes
    
    #endregion

    #region 臺中市所有公車路線編號
    def allBusID(self, busList): 
        
        busIDList=[]
        #region 迴圈記憶法
        '''
        tempID=''
        #buses=0        
        for i in busList:
            if tempID == '' or tempID != i[self.busID]:
                busIDList.append(i[self.busID])
                tempID=i[self.busID]
        #buses=len(busIDList)
        #print("臺中市公車共",buses,"條路線") 
        
        return busIDList
        '''
        #endregion
        
        for i in busList:
            busIDList.append(i[self.busID])
        
        
        return list(dict.fromkeys(busIDList))
    
    #endregion

    #region 臺中市所有公車路線名稱
    def allBusName(self, busList):
        
                
        busNameList=[]
        #region 迴圈記憶法
        '''
        tempBusName=''        
        for i in busList:
            tempList=[]
            if tempBusName == '' or tempBusName != i[self.busName]:
                tempList.append(i[self.busID])
                tempList.append(i[self.busName])
                busNameList.append(tempList)
                tempBusName=i[self.busName]         
        
        return busNameList      
        '''
        #endregion
        
        for i in busList:
            # if [i[self.busID],i[self.busName]] not in busNameList:
            #     busNameList.append([i[self.busID],i[self.busName]])
            self.unduplicateList(busNameList,[i[self.busID],i[self.busName]])
        return busNameList
                
        
    
    #endregion

    #region 路線去程站數量及回程站數量
    def allBusStopsNum(self, busList, busIDList):
        
        listStopsNum=[]    
        '''
        for i in range(len(busIDList)):
            listTemp=[]
            stopsOB=0
            stopsIB=0              
            for row in busList:
                if busIDList[i]==row[self.busID]:                    
                    if self.roundTrip_ob==row[self.roundTrip]:                
                        stopsOB+=1                         
                    if self.roundTrip_ib==row[self.roundTrip]:                        
                        stopsIB+=1                                      
            listTemp.append(busIDList[i])
            listTemp.append(stopsOB)
            listTemp.append(stopsIB)
            listStopsNum.append(listTemp)
        '''
        
        for i in busIDList:
            stopsOB=[]
            stopsIB=[]
            for row in busList:
                if i==row[self.busID]:
                    if self.roundTrip_ob==row[self.roundTrip]:                
                        stopsOB.append(row)                         
                    if self.roundTrip_ib==row[self.roundTrip]:                        
                        stopsIB.append(row)
            listStopsNum.append([i,len(stopsOB),len(stopsIB)])
            
        #串列[['路線'],去程站數量,回程站數量]    
        return listStopsNum
    #endregion

    #region 查站點名稱（中文/英文），暫時只有中文
    def searchStopName(self, lang, stopNameCN, stopNameEN, busList):
        
        stopsList=[]
        CN_Name=self.stopName_CN    
        EN_Name=self.stopName_EN
        stopName=""        
        langField=""        
        if lang=="CN":
            langField=CN_Name
            stopName=stopNameCN
        elif lang=="EN":
            langField=EN_Name
            stopName=stopNameEN            
        for i in busList:
            if stopName in i[langField]:
                stopsList.append(i)                
        return stopsList
    #endregion
    
    #region 非重覆清單，資料若已出現在清單中則不附加進
    #簡化用於去除重覆的記憶迴圈法
    def unduplicateList(self, appendToList, appendedData):
        
        if appendedData not in appendToList:
            #從未出現過才附加
            appendToList.append(appendedData)
        
    #endregion
    
    #region 自動去除重覆清單
    def autoUnduplicateList(self, duplicateList):
        return list({frozenset(item.items()): item for item in duplicateList}.values())
    #endregion
#endregion
