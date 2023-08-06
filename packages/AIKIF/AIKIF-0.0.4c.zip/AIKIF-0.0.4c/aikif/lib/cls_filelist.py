# -*- coding: utf-8 -*-
# cls_filelist.py
import os
import shutil
import csv
import glob
import fnmatch
import time
from datetime import datetime

def TEST():
    """ simple test used for development.
    TODO - move to unittest 
    TODO - check that folder is NOT a filename
    TODO - make sure folder passed is a LIST not a string
    TODO - make sure xtn passed is a LIST not a string
    TODO - make sure excluded is passed NOT just the output file
    TODO - decide whether you really need a FileListGroup or just
           an autobackup app class
    """
    print("Running self test for cls_filelist")
    fldr = os.path.dirname(os.path.abspath(__file__))
    
    fl_grp = FileListGroup("AIKIF lib files", fldr, "E:\\backup")
    print(fl_grp)
    
    fl = FileList([fldr], ['*.py'], [], "sample_filelist.csv")
    #col_headers = ["name", "size", "date", "path"]
    col_headers = ["name", "date", "size"]
    #col_headers = ["date", "fullfilename"]
    for f in fl.fl_metadata:
        #print('{:<30}'.format(f["name"]), '{:,}'.format(f["size"]))
        print(fl.print_file_details_in_line(f["fullfilename"], col_headers))
    print("Done.")
    
class FileListGroup(object):
    """ 
    not sure about the point of this class - might be simpler 
    to just get cls_filelist to do all the work. Will leave it in
    in case I remember the original idea
    """
    def __init__(self, name, src_folder, dest_folder):
        self.name = name
        self.filelist = []              # contains a list of the filelist class instances
        self.src_folder = src_folder
        self.dest_folder = dest_folder
     
    def __str__(self):
        """ display the filelist group details """
        txt =  'FileListGroup : ' + self.name + '\n'
        txt += 'src_folder    : ' + self.src_folder + '\n'
        txt += 'dest_folder   : ' + self.dest_folder + '\n'
        return txt
        
    def backup(self):
        """
        copies all files from the src folder to the dest folder
        """
        print("TODO backing up " + self.name)
        
    def restore(self):
        """
        restores all files from the dest folder to the src folder
        """
        print("TODO (be careful with this) restoring " + self.name)
        
    def backup_incremental(self):
        """
        copies CHANGED files from the src folder to the dest folder
        This is the primary mode of AutoBackup
        """
        print("TODO backing up changed files only " + self.name)

class FileList(object):
    def __init__(self, paths, xtn, excluded, output_file_name = 'my_files.csv'):
        self.output_file_name = output_file_name
        self.filelist = []       # list of full filenames
        self.fl_metadata = []    # dictionary of all file metadata
        self.fl_dirty_files = [] # list of fullfilenames needing to be backed up
        self.failed_backups = [] # list of files that failed to backup
        self.paths = paths
        self.xtn = xtn
        self.excluded = excluded
        
        self.get_file_list(self.paths, self.xtn, self.excluded)
    
    def get_list(self):
        return self.filelist

    def get_dirty_filelist(self):
        return self.fl_dirty_files

    def get_metadata(self):
        return self.fl_metadata
    

    def get_failed_backups(self):
        return self.failed_backups

    def add_failed_file(self, fname, dest_folder):
        """ this file failed to backup, so log it for future retry """
        self.failed_backups.append(fname)
        
    def check_files_needing_synch(self, dest_root_folder, base_path_ignore, date_accuracy = 'hour'):
        """ 
        checks the metadata in the list of source files
        against the dest_folder (building path) and flags a
        data_dirty column in the metadata if the file needs
        backing up.
        """
        for f in self.fl_metadata:
            dest_folder =  os.path.join(dest_root_folder, os.path.dirname(f["fullfilename"])[len(base_path_ignore):])
            dest_file = dest_folder + os.sep + f["name"]
            # works - find correct source file and dest file
            #print("Checking file - " + f["fullfilename"])
            #print("against dest_file = " + dest_file)
            if self.is_file_dirty(f, dest_file, date_accuracy):
                self.fl_dirty_files.append(f["fullfilename"])
                
    
    def is_file_dirty(self, src_file_dict, dest_file, date_accuracy):
        """ 
        does various tests based on config options (eg simple
        date modified, all files, check CRC hash
        """
        try:
            if os.path.isfile(dest_file) == False:
                return True  # no backup exists, so needs backing up
        except:
            pass

        try:
            if src_file_dict["size"] != os.path.getsize(dest_file):
                return True  # file size has changed, so backup
        except:
            pass
        
        try:
            if self.compare_file_date(src_file_dict["date"], dest_file, date_accuracy) == False:
                return True  # file date is different so MAYBE backup
        except:
            pass
         
        try:
            if self.get_file_hash(src_file_dict["fullfilename"]) != self.get_file_hash(dest_file):
                return True   # file contents changed so backup (e.g. fixed file sizes)
        except:
            pass
        
        # all tests pass, so assume file is ok and doesn't need syncing    
        
        return False
    
    def get_file_hash(self, fname):
        """ returns a file hash of the file """
        return 1  # not implemented obviously - should used saved results anyway
    
    def compare_file_date(self, dte, dest_file, date_accuracy):
        """Checks to see if date of file is the same   """
        dest_date = self.GetDateAsString(os.path.getmtime(dest_file))
        
        date_size = 17
        if date_accuracy == 'day':
            date_size = 11
        if date_accuracy == 'hour':
            date_size = 13
        if date_accuracy == 'min':
            date_size = 15
            
        # now trunc both date strings by same amount
        #print("dte before = " + dte)
        dest_date = dest_date[:date_size]
        dte  = dte[:date_size]
        #print("dte after  = " + dte)
        # TODO = take into account time differences on other servers
        # do this once at calling function by creating a file and 
        # checking timestamp against sysdate and then getting an offset
        # (usually .5 to 1 hour difference max)
        
        if dte != dest_date:
            return False
        return True
        
    def get_file_list(self):
        """
        uses self parameters if no parameters passed - TODO - add test for this!!!!
        """
        self.get_file_list(self, self.paths, self.xtn, self.excluded)
        
    def get_file_list(self, lstPaths, lstXtn, lstExcluded, VERBOSE = False):
        """
        builds a list of files and returns as a list 
        originally from lib_file.py in aspytk
        """
        if VERBOSE:
            print("Generating list of Files...")
            print("Paths = ", lstPaths)
            print("Xtns  = ", lstXtn)
            print("exclude = ", lstExcluded)
        numFiles = 0    
        self.filelist = []
        self.fl_metadata = []
        for rootPath in lstPaths:
            if VERBOSE:
                print(rootPath)
            for root, dirs, files in os.walk(rootPath):
                for basename in files:
                    for xtn in lstXtn:
                        if fnmatch.fnmatch(basename, xtn):
                            filename = os.path.join(root, basename)
                            includeThisFile = "Y"
                            if len(lstExcluded) > 0:
                                for exclude in lstExcluded:
                                    if filename.find(exclude) != -1:
                                        includeThisFile = "N"
                            if includeThisFile == "Y":
                                if VERBOSE:
                                    try:
                                        print(os.path.basename(filename), '\t', os.path.getsize(filename))
                                    except:
                                        print("ERROR printing UniCode filename")
                                numFiles = numFiles + 1
                                self.filelist.append(filename)
                                self.add_file_metadata(filename)    # not sure why there is a 2nd list, but there is.
                        else:
                            try:
                                #print("file not matched " + basename)
                                pass
                            except:
                                print("file not matched, but cant print basename")
        if VERBOSE:
            print("Found ", numFiles, " files")
        return self.filelist

    def add_file_metadata(self, fname):
        file_dict = {}
        file_dict["fullfilename"] = fname
        file_dict["name"] = os.path.basename(fname)
        file_dict["date"] = self.GetDateAsString(os.path.getmtime(fname))
        file_dict["size"] = os.path.getsize(fname)
        file_dict["path"] = os.path.dirname(fname)
        self.fl_metadata.append(file_dict)

    def print_file_details_in_line(self, fname, col_headers):
        """ makes a nice display of filename for printing based on columns passed 
               print('{:<30}'.format(f["name"]), '{:,}'.format(f["size"]))
        """
        line = ''
        for fld in col_headers:
            if fld == "fullfilename":
                line = line + fname
            if fld == "name":
                line = line + '{:<30}'.format(os.path.basename(fname)) + ' '
            if fld == "date":
                line = line + self.GetDateAsString(os.path.getmtime(fname)) + ' '
            if fld == "size":
                line = line + '{:,}'.format(os.path.getsize(fname)) + ' ' 
            if fld == "path":
                line = line + os.path.dirname(fname) + ' '
        #line += '\n'
        return line
        
    def print_file_details_as_csv(self, fname, col_headers):
        """ saves as csv format """
        line = ''
        qu = '"'
        d = ','
        for fld in col_headers:
            if fld == "fullfilename":
                try:
                    line = line + qu + fname + qu + d
                except:
                    line = line + qu + 'ERROR_FILENAME' + qu + d
            if fld == "name":
                try:
                    line = line + qu + os.path.basename(fname) + qu + d
                except:
                    line = line + qu + 'ERROR_FOLDER' + qu + d
            if fld == "date":
                try:
                    line = line + qu + self.GetDateAsString(os.path.getmtime(fname)) + qu + d
                except:
                    line = line + qu + 'ERROR_DATE' + qu + d
            if fld == "size":
                try:
                    line = line + qu + str(os.path.getsize(fname)) + qu + d
                except:
                    line = line + qu + 'ERROR_SIZE' + qu + d
            if fld == "path":
                try:
                    line = line + qu + os.path.dirname(fname) + qu + d 
                except:
                    line = line + qu + 'ERROR_PATH' + qu + d
                   
        #line += '\n'
        return line
        
    def GetDateAsString(self, t):
        res = ''
        try:
            res = str(datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))
        except:
            pass
        return res     
        
    def TodayAsString(self):	
        """
        returns current date and time like oracle
    #	return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        
        
    def save_filelist(self, opFile, opFormat, delim=',', qu='"'):
        """
        uses a List of files and collects meta data on them and saves 
        to an text file as a list or with metadata depending on opFormat.
        """
        with open(opFile,'w') as fout:
            fout.write("fullFilename" + delim)
            for colHeading in opFormat:
                fout.write(colHeading + delim)
            fout.write('\n')    
            for f in self.filelist:
                line = qu + f + qu + delim
                try:
                    for fld in opFormat:
                        if fld == "name":
                            line = line + qu + os.path.basename(f) + qu + delim
                        if fld == "date":
                            line = line + qu + self.GetDateAsString(os.path.getmtime(f)) + qu + delim 
                        if fld == "size":
                            line = line + qu + str(os.path.getsize(f)) + qu + delim
                        if fld == "path":
                            line = line + qu + os.path.dirname(f) + qu + delim
                except:
                    line += '\n'   # no metadata
                try:
                    fout.write (line + '\n')
                except:
                    print("Cant print line - cls_filelist line 304")
                    
            #print ("Finished saving " , opFile)

	
    def save_file_usage(self, fldr, nme):
        """ saves a record of used files for infolink applications """
        print("Saving File Usage to " + fldr)
        #print(self.get_dirty_filelist())
        file_copied = fldr + 'copied_' + nme + '.txt'
        file_failed = fldr + 'failed_' + nme + '.txt'
        file_data = fldr + 'filelist_' + nme + '.csv'
        file_usage = fldr + 'file_usage.csv'
        
        if os.path.isfile(file_copied):
            os.remove(file_copied)
        with open(file_copied, 'w', encoding='utf-8') as f:
            f.write("# Backed up on " + self.TodayAsString() + '\n')
            for fname in self.get_dirty_filelist():
                try:
                    f.write(fname + '\n')
                except:
                    print("FAILED LOGGING FILENAME to file_copied")
                
        if os.path.isfile(file_failed):
            os.remove(file_failed)
        with open(file_failed, 'w', encoding='utf-8') as f:
            f.write("# Files Failed to backup on " + self.TodayAsString() + '\n')
            for fname in self.get_failed_backups():
                try:
                    f.write(fname + '\n')
                except:
                    print("FAILED LOGGING FILENAME to file_failed")
                
        if os.path.isfile(file_data):
            os.remove(file_data)
        with open(file_data, 'w', encoding='utf-8') as f:
            f.write("# FileList refreshed on " + self.TodayAsString() + '\n')
            for fname in self.get_list():
                try:
                    f.write(self.print_file_details_as_csv(fname, ["name", "size", "date", "path"] ) + '\n')
                except:
                    print("FAILED LOGGING FILENAME to file_data")
            
        with open(file_usage, 'a', encoding='utf-8') as f:
            for fname in self.get_dirty_filelist():
                try:
                    f.write(self.TodayAsString() + ', ' + fname + ' (' + str(os.path.getsize(fname)) + ' bytes)\n')
                except:
                    print("FAILED LOGGING FILENAME to file_usage")

 
    def update_indexes(self, fname):
        """ 
        updates the indexes in AIKIF with any changed files.
        This uses the same process as main metdatalist - check to see if date of index
        is old, THEN update index for that file and call consolidate index
        """
        print("Updating index " + fname)
        
        
	
if __name__ == '__main__':
	TEST()
	
            