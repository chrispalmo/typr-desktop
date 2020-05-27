# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 21:32:47 2017

@author: chrispalmo
"""
from tkinter import *
from tkinter import font
from tkinter import filedialog

import threading
import time
from ebooklib import epub

from typr import EpubLoader
from typr import BookmarkLoader
from typr import StatsManager

class typr(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.version = 'Typr v1.0'
        self.book = None
        self.last_book = None
        self.win_width = 60 #width of window
               
        self.initialize_frame()
        
        self.focus_force()
        self.txtbox.focus()

        self.charpos=0
        self.stats=StatsManager.StatsManager()
           
    def initialize_frame(self):
        print("Initialising application...")
                
        #Menu
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        
        self.filemenu = Menu(self.menubar)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open", command=self.open_file)
        self.filemenu.add_command(label="Exit", command=self.close)
        
        #Frame Layout
        self.text_frame = Frame(self)
        self.text_frame.pack(fill=BOTH)

        self.timer_wpm_frame = Frame(self)
        self.timer_wpm_frame.pack(fill=BOTH)

        self.timer_frame = Frame(self.timer_wpm_frame)
        self.timer_frame.pack(side=LEFT, fill=BOTH)

        self.wpm_frame = Frame(self.timer_wpm_frame)
        self.wpm_frame.pack(side=RIGHT, fill=BOTH)

        self.navpanel = NavPanel(self)
        
        #Caps Lock Warning
        self.caps_lbl = Label(self.timer_wpm_frame, text="")
        
        #Font options
        self.active_font = font.Font(family="courier",size=12)
        self.txtbox = Text(self.text_frame,
                           height=12,
                           width=self.win_width,
                           font=(self.active_font.cget("family"),
                                 self.active_font.cget("size")),
                           wrap=WORD)
        self.txtbox.pack(side = LEFT, fill=Y)
        self.txtbox.configure(state="disabled")
        self.txtbox.bind("<Key>", self.keypress)
        
        #Load text
        self.load_text()
        
        #Set up font formats        
        self.txtbox.tag_configure("grey_tag", 
                                  font=self.active_font, 
                                  foreground="grey")
        self.txtbox.tag_configure("red_tag", 
                                  font=self.active_font, 
                                  foreground="red",
                                  background="pink")

        #Scrollbar
        self.scrollbar =  Scrollbar(self.text_frame)
        self.scrollbar.config(command=self.txtbox.yview)
        self.scrollbar.pack(side = RIGHT, fill=Y)

        #Timer Display
        self.timer_disp = Label(self.timer_frame)
        self.timer_disp.configure(text="Timer")
        self.timer_disp.pack()
        
        #Initialize timer
        self.idle_time_limit=1
        timer_thread = threading.Thread(name="timer_thread", target=self.timer)
        timer_thread.start()

        #WPM Display
        self.wpm_disp = Label(self.wpm_frame)
        self.wpm_disp.configure(text="WPM: 78")
        self.wpm_disp.pack()
        
    def timer(self):
        self.idle_time = 0
        total_time_elapsed = 0
        interval = 1/10
        while True:
            #if idle_time < self.idle_time_limit:
            while self.idle_time > self.idle_time_limit:
                time.sleep(interval)
            while self.idle_time < self.idle_time_limit:
                self.idle_time += interval
                total_time_elapsed += interval
                total_time_elapsed_str = 'Timer: {0:.{1}f}'.format(total_time_elapsed, 1)
                self.timer_disp.configure(text=total_time_elapsed_str)
                time.sleep(interval)
            total_time_elapsed_str += ' [PAUSED]'
            self.timer_disp.configure(text=total_time_elapsed_str)
        return None

    def open_file(self):      
        self.book = EpubLoader.EpubLoader(self)
        if self.book.file == None:
            return None
        self.wm_title = (self,self.version+" "+self.book.bookfilename)
        self.navpanel.update(self)
        
        #load bookmark position for book
        self.bm_loader = BookmarkLoader.BookmarkLoader(self)

        if self.bm_loader.load_bm(self) != None:
            self.goto_para(self.bm_loader.load_bm(self))
        self.load_text()
    
    def next_para(self):
        self.book.next_para()
        self.load_text()
        self.navpanel.update(self)
        self.bm_loader.save_bm(self)      
        self.stats.save()
        
    def prev_para(self):
        self.book.prev_para()
        self.load_text()
        self.navpanel.update(self)
        self.bm_loader.save_bm(self)
        
    def goto_para(self, page_num):
        self.book.goto_para(page_num)
        self.load_text()
        self.navpanel.update(self)
        self.bm_loader.save_bm(self)
    
    def load_text(self):
        if self.book == None:
            self.open_file()
        
        if self.book.file == None:
            return None
            
        self.txtbox.configure(state="normal")
        self.txtbox.delete('1.0', END)
        
        if len(self.book.get_para()) == 0:
            self.book.next_para()
            self.load_text()
            return None
        
        for char in self.book.get_para():
            self.txtbox.insert(END, char)
        self.txtbox.configure(state="disabled")
        self.txtbox.focus_force()
        self.charpos=0
        
    def keypress(self, event):
        self.idle_time = 0
          
        if event.keycode == 16: return None #shift key is ignored
        if event.keycode == 17: return None #ctrl key is ignored

        #Left and right Arrow keys
        if event.keycode == 37:
            self.prev_para()
            return None
        if event.keycode == 39:
            self.next_para()
            return None
        
        #Caps
        if event.keycode == 20:
              if event.state == 0:
                    self.caps_lbl.configure(text="WARNING: Caps Lock is ON", background="red")
                    self.caps_lbl.pack()
                    return None
              else:
                    self.caps_lbl.configure(text="")
                    self.caps_lbl.pack_forget()
                    return None
        
        #Set Selection
        self.txtbox.configure(state="normal")
        self.txtbox.tag_remove(SEL,"1.0",END)
        self.txtbox.tag_add(SEL,
                            "1."+str(self.charpos),
                            "1."+str(self.charpos+1))
        #Backspace
        if event.keycode == 8:
            self.move_cursor("backwards")
            self.txtbox.tag_remove("grey_tag", "sel.first", "sel.last")
            self.txtbox.tag_remove("red_tag", "sel.first", "sel.last")
            self.txtbox.configure(state="disabled")
            return None
     
        #All other keys
        selection = self.txtbox.selection_get() 
        if event.char == selection:
            #Update accuracy stats            
            if self.stats.counts.get(selection)==None: self.stats.counts[selection]=[1, 0]
            else: self.stats.counts[selection][0] += 1
            self.stats.add(selection,event.char,True)
            
            #format text, move cursor
            self.txtbox.tag_add("grey_tag", "sel.first", "sel.last") 
            self.move_cursor("forwards")
            self.txtbox.configure(state="disabled")           
            return None
            
        else:
            #Update accuracy stats 
            if self.stats.counts.get(selection)==None: self.stats.counts[selection]=[0, 1]
            else: self.stats.counts[selection][1] += 1
            self.stats.add(selection,event.char,False)

            #format text, move cursor
            self.txtbox.tag_add("red_tag", "sel.first", "sel.last")
            self.move_cursor("forwards")
            self.txtbox.configure(state="disabled")
            return None
        
    def move_cursor(self, direction):
        if direction == "forwards":
            if self.charpos == len(self.book.get_para())-1:
                print ("cursor is at the end of the paragraph")
                self.next_para()
                return None
            else:   
                self.charpos += 1
                self.txtbox.tag_remove(SEL,"1.0",END)
                self.txtbox.tag_add(SEL,
                                    "1."+str(self.charpos),
                                    "1."+str(self.charpos+1))
        if direction == "backwards":
            if self.txtbox.index("sel.first") == "1.0":
                print ("cursor is at the start of the paragraph")
                return None
            else:
                #Move cursor
                self.charpos -= 1
                self.txtbox.tag_remove(SEL,"1.0",END)
                self.txtbox.tag_add(SEL,
                                    "1."+str(self.charpos),
                                    "1."+str(self.charpos+1))        
    def close(self):
        self.destroy()
        return None

class NavPanel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack(fill=BOTH)

        BUTTON_WIDTH = 5
        self.prev_bt = Button(self, text="◀", width=BUTTON_WIDTH,
                         command=master.prev_para)
        self.prev_bt.pack(side=LEFT)
        self.next_bt = Button(self, text="▶", width=BUTTON_WIDTH,
                         command=master.next_para)
        self.next_bt.pack(side=RIGHT)
        
        self.centreframe = Frame(self)
        self.centreframe.pack()
        
        self.pagecount_lbl = Label(self.centreframe, text="")
        self.pagecount_lbl.pack(side=RIGHT)
        
        self.goto_entry = Entry(self.centreframe, width=0)
        self.goto_entry.bind('<KeyRelease>', self.entry_keypress)
        self.goto_entry.bind('<Button-1>', self.entry_select)
        self.centreframe.bind()
        self.goto_entry.pack(side=RIGHT)
        
    def goto(self, event):
        page_num = int(self.goto_entry.get())
        self.master.goto_para(page_num)
        self.update(self.master)

    def entry_keypress(self, event):
        #Backspace or Delete
        if event.keycode == 8 or event.keycode == 46:
            self.goto_entry.configure(width=len(str(self.goto_entry.get())))
        #Enter
        if event.keycode == 13:
            self.goto(event)
        else:
            self.goto_entry.configure(width=len(str(self.goto_entry.get()))+1)

    def entry_select(self, event):
        self.goto_entry.select_range(0,'end')
           
    def update(self, master):
        percent = master.book.pos/len(master.book.content)*100
        percent_str = '{0:.{1}f}'.format(percent, 2)+'%'
        self.pagecount_lbl.configure(
                text="/"+str(len(master.book.content))+" ("+percent_str+")")
        self.goto_entry.delete(0,len(self.goto_entry.get()))
        self.goto_entry.insert(0, master.book.pos)
        self.goto_entry.configure(width=str(1+len(str(self.goto_entry.get()))))
          
if __name__ == "__main__":
    root = typr()
    root.title("typr")
    root.iconbitmap('icon.ico')
    root.mainloop()



