# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 21:32:47 2017

@author: chrispalmo
"""
from pylab import matplotlib
from scipy import *
import matplotlib.pyplot as plt

import pickle
import os
import datetime
import StatsManager
import csv

def wpm(raw_data,threshold):
    data=raw_data.copy()
    for i in range(len(data)):
        if i > 0: 
            if data[i][3]-data[i-1][3] < threshold:
                data[i].append(data[i][3]-data[i-1][3])
            else:
                data[i].append(0)
        else:
            data[i].append(0)
    return data

def moving_avg(data,width,threshold):
    x=[i[3] for i in data]
    dt=[]
    for i in range(len(data)):
        if i > 0: 
            if data[i][3]-data[i-1][3] < threshold:
                dt.append(data[i][3]-data[i-1][3])
            else:
                dt.append(0)
        else:
            dt.append(0)
    
    #wpm (avg 5 chars per word)
    y=[]
    for i in dt:
        if i == 0:
            y.append(0)
        else:
            y.append(1/i*60/5)

    plt.style.use('ggplot')
    font = {'size':25}
    matplotlib.rc('font', **font)

    plot = plt.scatter(x, y, s=size)  
    plt.xlabel("Timestamp")
    plt.ylabel("Average WPM")
    plt.axes = plt.gca()
    plt.show()  
    
    return [x,y]
            
def accuracy_per_char(data):
    data=wpm(data,1) #ignore time gaps greater than 1 second
    
    #compile a list of each unique character encountered
    chars=[]
    for row in data:
        if row[0] not in chars:
            chars.append(row[0])
    chars=sorted(chars)

    #append accuracy stats for each unique character
    char_stats=[]
    for char in chars:
        char_stats.append([char])
    
    for char in char_stats:
        correct=0
        incorrect=0
        spc=[]
        for row in data:
            if row[0] == char[0]:
                if row[2] == True:
                    correct+=1
                else:
                    incorrect+=1
                #update average seconds per character
                if row[4] > 0:
                    spc.append(row[4])
        char.append(correct)
        char.append(incorrect)
        char.append(correct+incorrect)
        accuracy_percent=100*(1-incorrect/(correct+incorrect))
        char.append(round(accuracy_percent,2))
        try:
            avg_spc = sum(spc)/float(len(spc))
            avg_wpm = 1/avg_spc*60/5
            char.append(round(avg_wpm,2))
        except Exception as e:
            print(e)
            char.append(0)

    return sorted(char_stats, key=lambda x : x[1])
    
def export_csv(data, filename):  
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def bubble_plot(data):
    plt.style.use('ggplot')
    font = {'size':25}
    matplotlib.rc('font', **font)
    
    x = [round(i[4]) for i in data] #accuracy
    y = [round(i[5]) for i in data] #WPM
    labels = [i[0] for i in data]
    size = [i[3]**0.75 for i in data] #sample size
    
    plot = plt.scatter(x, y, s=size)  
    plt.xlabel("Accuracy (%)")
    plt.ylabel("Average WPM")
    plt.axes = plt.gca()
    plt.show()
