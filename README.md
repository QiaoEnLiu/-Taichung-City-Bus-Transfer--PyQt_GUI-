哈囉！你好嗎？


![image](/Resource/中興幹線.png)


公車系統轉乘PyQt5圖形化介面

	臺中市公車資料集轉乘分析(Taichung City Bus Transfer)

當乘客要撘乘公車前往目的地時，發現可抵達目的地的公車沒有經過乘客當下的站點，於是乘客就可以決定撘乘到可以換乘直達目的地站點的公車，此方式為轉乘；而此專案則是使用臺中市市政府開放資料平台​的「臺中市市區公車站牌資料」分析出轉乘組合，如果要從朝陽科大前往逢甲大學就​可以列出「131(朝陽科技大學-臺中火車站)25(臺中火車站-逢甲大學）」這其中一種轉乘組合。

此專案由Python撰寫，使用Anaconda-Spyder環境以「朝陽科技大學」前往「逢甲大學（福星路）」測試，在輸入撘乘站點及目的站點後，先判斷是否可以直達，不可直達則輸出轉乘組合。


	Resource資料夾：臺中市公車站牌資料集（離線）

	臺中市市區公車站牌資料載點網頁： https://opendata.taichung.gov.tw/search/3e09d847-0fbd-41fa-9e6c-2b37aa47e07e

	參考專案： https://github.com/QiaoEnLiu/-Taichung-City-Bus-Transfer-
	
 
	Resource資料夾：臺中市公車站牌資料集及其他資源
	ui資料夾：以Qt Designer建立的PyQt5檔案資料夾
	Bus_OOP.py：適用於本專案的自建函數
	FilePath_OOP.py：檔案路徑、檔名、副檔名組合
	searchBus.py：查詢公車圖像化介面
	takeBus.py：主程式圖像化介面，從現在撘乘站前往目的地可撘哪些公車
 	劉喬恩_臺中市公車系統轉乘組合PyQt5（簡報）.pdf：PDF簡報檔

