# -*- coding: utf-8 -*-
"""
Created on Wed May 17 11:45:11 2023

@author: User
"""
class FilePath:
    
    def __init__(self,file,ext):
        
        self.dir='Resource/' #檔案路徑
        self.file=file #檔名
        self.ext='.'+ext #副檔名
        
    def path(self):
            
        return self.dir+self.file+self.ext