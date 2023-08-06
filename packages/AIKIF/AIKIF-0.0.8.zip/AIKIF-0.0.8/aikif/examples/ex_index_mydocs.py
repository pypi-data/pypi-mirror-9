# coding: utf-8
# ex_index_mydocs.py	written by Duncan Murray 22/5/2014
# Example program to index all personal data for keyword searches using AIKIF.
# Source data is taken from Acute Softwares Diary and FileLister

import os
import sys
import aikif.index as ndx
import aikif.config as mod_cfg
import aikif.lib.cls_filelist as mod_fl

  
local_folder = mod_cfg.fldrs['pers_data'] + os.sep + 'diary' + os.sep
diary_folder = 'C:\\APPS\\netDiary\\data'

manual_files_to_index = [
    local_folder + 'diary_Ent_duncan.txt',
    local_folder + 'lf_folders.csv',
    local_folder + 'lf_files.csv'
    ]

delims = [' ', '\\', '/', '_']

ndxFile = 'T:\\user\\AIKIF\\pers_data\\ndx_temp.txt'
ndxFile_final = 'T:\\user\\AIKIF\\pers_data\\ndx_final.txt'

def main():
    try:
        os.remove(ndxFile)
    except:
        pass
    all_files = add_diary_files_to_list(manual_files_to_index, diary_folder)	
    numFiles = 0
    for f in all_files:
        try:
            numFiles += 1
            print('indexing ', str(numFiles) , ' of ', str(len(all_files)), ' : ', f)
            ndx.buildIndex(f, ndxFile, 'Y', 'N')	# run the index routine
        except:
            print('ERROR - cant index file ', f)

    print('consolidating.... ')		
    ndx.consolidate(ndxFile, ndxFile_final)	
    print('Done!')		

def add_diary_files_to_list(lst, fldr):
    """ adds all Diary files from folder to the lst   """
    fl = mod_fl.FileList([fldr], ['D2014*.DAT'], ["__pycache__", ".git"], "temp.csv")
 
    for f in fl.get_list():
        lst.append(f)
    return lst
    
if __name__ == '__main__':		
    main()
