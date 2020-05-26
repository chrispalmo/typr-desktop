# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 10:45:08 2017

@author: Chris Palmieri
"""

import pickle

class BookmarkLoader(object):
   
    def __init__(self, master):
        self.bm_dict=self.load_bm(master)
    
    def save_bm(self, master):
        self.bm_dict.update({master.book.bookfilename:master.book.pos})
        pickle.dump(self.bm_dict,open("bookmarks.txt","wb"))
        
    def load_bm(self,master):
        try:
            self.bm_dict = pickle.load(open("bookmarks.txt","rb"))
            return self.bm_dict[master.book.bookfilename]
        except Exception as e:
            print("\nBookmarkLoader Error #1:\n")
            print(e)
        
if __name__ == "__main__":
#    print('creating root window...')
#    root = Tk()
#    print('creating BookmarkLoader` object...')
#    book = EpubLoader(root)    
    pass