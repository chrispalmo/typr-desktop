# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 10:45:08 2017

@author: Chris Palmieri
"""

import pickle
import os
import datetime

class StatsManager(object):
   
    def __init__(self):
        self.counts = {}
        self.data = []
        self.load()
        self.temp=[]
        self.inst_wpm = 0
        
#    def save(self):
#        
#        date = datetime.datetime.now()
#        
#        if len(str(date.day)) == 1:
#            day_str = "0"+str(date.day)
#        else:
#            day_str = str(date.day)
#        date_str = filename = str(date.year)+str(date.month)+day_str
#        filename = date_str+".stats"
#        print("Saving file:",filename)
#        
#        pickle.dump(self.data,open(date_str+".stats","wb"))
#        
#    def load(self):
#        try:
#            print("loading",self.latest_file_date(),".stats")
#            self.data = pickle.load(open(str(self.latest_file_date())+".stats","rb"))
#            #print(self.data)
#        except Exception as e:
#            print("\nStatsLoader Error:\n")
#            print(e)

    def save(self,filename=""):
        if filename == "":
            date = datetime.datetime.now()
            
            if len(str(date.day)) == 1:
                day_str = "0"+str(date.day)
            else:
                day_str = str(date.day)
            date_str = filename = str(date.year)+str(date.month)+day_str
            filename = date_str+".stats"
            print("Saving file:",filename+".stats")
            
            pickle.dump(self.data,open(date_str+".stats","wb"))
        else:
            print("Saving file:",filename+".stats")
            pickle.dump(self.data,open(filename+".stats","wb"))
        
    def load(self,filename=""):
        if filename == "":
            try:
                print("loading",str(self.latest_file_date())+".stats")
                self.data = pickle.load(open(str(self.latest_file_date())+".stats","rb"))
                #print(self.data)
            except Exception as e:
                print("\nAnalyser Error:\n")
                print(e)
        else:
            try:
                print("loading",self.latest_file_date(),".stats")
                self.data = pickle.load(open(filename+".stats","rb"))
                #print(self.data)
            except Exception as e:
                print("\nAnalyser Error:\n")
            print(e)
    
    def latest_file_date(self):        
        statfiles = []
        for file in os.listdir():
            if file.endswith(".stats"):
                statfiles.append(file)
        filedates = [int(file[:8]) for file in statfiles]
        return max(filedates)
    
    def add(self,correct_symbol,typed_symbol,correct):
        self.data.append([correct_symbol,
                          typed_symbol,
                          correct,
                          datetime.datetime.now().timestamp()])
        try:
            self.update_inst_wpm(50,2)
            print("WPM ("+str(self.chars)+" char Avg. =\t",
                        round(self.get_inst_wpm()))
        except Exception as e:
            print(e)

    def update_inst_wpm(self, n, threshold):
        if n == 0:
            self.inst_wpm = 0
            return None
        self.dt=[]
        for i in range(-n,0):
            self.dt.append([self.data[i][2],
                            self.data[i][3],
                            self.data[i][3]-self.data[i-1][3]])
        if max([i[2] for i in self.dt]) > threshold:
            self.update_inst_wpm(n-1,threshold)
            return None
        else:
            seconds = self.dt[-1][1]-self.dt[0][1]
            self.chars = 0
            for i in self.dt:
                if i[0] == True:
                    self.chars += 1
            self.inst_wpm = self.chars/seconds*60/5
#            print("seconds=",seconds)
#            print("chars=",chars)
            return None
    
    def get_inst_wpm(self):
        return self.inst_wpm    

if __name__ == "__main__":
    stats=StatsManager()
    stats.update_inst_wpm(15,2)
    print("inst_wpm=",stats.get_inst_wpm())
    print("dt=",stats.dt)
    pass