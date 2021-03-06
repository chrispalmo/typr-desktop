# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 10:45:08 2017

@author: Chris Palmieri
"""

import tkinter
from tkinter import filedialog
from tkinter import *
from bs4 import BeautifulSoup
import zipfile
import pickle

class EpubLoader(object):
    """Stores a user-selected EPUB file 
    as a list of chapters, each containing
    a list of paragraphs"""
    
    def __init__(self, master):
        master.focus_force()

        self.content=[]
        
        if master.last_book == None:
            self.file = tkinter.filedialog.askopenfile(parent=master,
                                                       mode='rb',
                                                       title='Choose a file')
        else:
            self.file = open(master.last_book,'rb')
            
        if self.file != None:
            try:
                z = zipfile.ZipFile(self.file,"r")
                self.bookfilename = self.file.__str__().split("/")[-1].split("'>")[0]
                print("Loading "+self.bookfilename+"...")
                print("Loading chapters...")
                self.chapter_names = []
                self.chapters_soup = []
            
                #look for pre-processed txt file
                self.load_txt(master)
                print("Book successfully loaded from .txt file")
#                
                if len(self.content) == 0:
                    #No pre-processed txt file exiSTS
                    for filename in z.namelist():
                        if filename[-4:]=="html":
                            print("Loading "+filename)
                            self.chapter_names.append(filename)
                            #chapters_html.append(z.read(filename))
                            self.chapters_soup.append(BeautifulSoup(z.read(filename),"lxml"))                                         
                    self.file.close()
                    self.content = self.get_tags("p")
                    print ("Book succesfully loaded.")
            except Exception as e:
                print("Error epl83:", e)
                self.file.close()
                self.file = None
                return None
                
        self.pos = 0
        self.pos_percent = 0
        self.length = len(self.content)
        
        try:
            self.save_txt(master)
        except Exception as e:
            print("\nCouldn't save .txt file:\n")
            print(e)
        
    def save_txt(self, master):
        pickle.dump(self.content,open(self.bookfilename+".txt","wb"))
        
    def load_txt(self,master):
        try:
            self.content = pickle.load(open(self.bookfilename+".txt","rb"))
        except Exception as e:
            print("\nEpubLoader Error #1:\n")
            print(e)
    
    def get_para(self):
        return self.content[self.pos]
    
    def next_para(self):
        if self.pos+1 < self.length:
            self.pos += 1
        
    def prev_para(self):
        if self.pos > 0:
            self.pos -= 1
            
    def goto_para(self, page_num):
        if type(page_num) == int:
            self.pos = page_num
       
    def get_chapternames(self):
        """returns a list of the titles of .xhtml files within the .EPUB file"""
        return self.chapter_names
    
    def get_chapters_soup(self):
        """returns a list containing the BeautifulSoup xhtml object
        for each chapter (i.e each .xhtml file within the .EPUB file)"""
        return self.chapters_soup
    
    def get_bookfilename(self):
        """returns the name of the .EPUB file"""
        return self.bookfilename
    
    def get_tags(self, tag):
        """returns a list of lists containing only items bound by <tag>,
        for each chapter (i.e each .xhtml file within the .EPUB file)"""
        chapters_tagged=[]
        for ch_soup in self.chapters_soup:
            chapters_tagged += [ch_soup.find_all(tag)[i].contents[0] for i in range(len(ch_soup.find_all(tag)))]      
            #clean up unwanted newlines
            try: 
                for i in range(len(chapters_tagged)):
                    if chapters_tagged[i] != None:
                        chapters_tagged[i]=" ".join(chapters_tagged[i].split("\n"))
            except Exception: 
                pass
            
        return chapters_tagged
