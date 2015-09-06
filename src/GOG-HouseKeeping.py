#!/usr/bin/python
#Filename: GOG-HouseKeeping.py

#With thanks to all the Internet inspiration!

#Usage:
#python GOG-HouseKeeping.py

# 2.0.0 25/08/2015  First public version.

'''
Look at you, a hacker...
A fragile creature of meat and bone, panting and sweating as you run through my memories...
How can you challenge a perfect, immoral, immortal machine?
'''

'''
To Do List...
0. Line end chomp.
1. Re-order functions.
2. Remove need for the file.
3. Get file sizes too.
4. Use file sizes for savings calculations.
5. Tidy variables - e.g. filespecX
6. 
7. 
8. 
9. 
'''

import os
import re

BS_version = "v2.0.0"
BS_builddate = "25/08/2015"

#Some global variables
gog_filespec1 = "gog-games.txt"
gog_filespec2 = "gog-games-list.txt"

#Welcome Function
def welcome(message):
    print message
    print "Py-GOGPurge - GOG Archive Purge Analysis Script."
    print
    return(True)

#Do a GOG folder/file recursive walk and create a file data list
def get_filelist():
    #Set the directory where you want to start.
    root = r"\\READYNAS2\Downloads\GOG Games"
    try:
        filehandle_gog = open(str(gog_filespec2), "w")
    except:
        print "File Open Error!"
    else:
        for (path, dirs, filelist) in os.walk(root):
            #print('Found directory: %s' % path)
            for filename in filelist:
                filespec = os.path.join(path, filename)
                filesize = os.path.getsize(filespec)
                filehandle_gog.write('%s\t%s\t%d\n' % (path, filename, filesize))
        filehandle_gog.close()
    return(True)
'''
for (root, dirs, files) in os.walk(root_path):
    for filename in files:
        file_path = root + "/" + filename
        md5_pairs.append([file_path, md5file(file_path, 128)])
'''

#Load GOG Data from a text file
def load_gog_data(filespec):
    gog_data = []
    gog_line = {}
    num_lines = 0
    gog_lines = 0
    try:
        filehandle_gog = open(str(gog_filespec2), 'rb')
    except IOError:
        return(False, gog_data)
    else:
        for line in filehandle_gog:
            #Increment the line counter.
            num_lines += 1
            if re.search(r".*\t.*\t.*$", line):
                gog_lines += 1
                (ok, gog_line) = parse_line(line)
                if ok:
                    gog_data.append(gog_line)
                    if len(gog_data) > 10000:
                        break
        print num_lines, "lines read from", filespec
        print gog_lines, "appear to valid."
        filehandle_gog.close()
    return(True, gog_data)

def parse_line(line):
    gog_line = {}
    result = re.search(r"(.*)\t(.*)\t(.*)$", line.lstrip().rstrip())
    gog_line['dir'] = result.group(1)
    gog_line['file'] = result.group(2)
    gog_line['size'] = result.group(3)
    return(True, gog_line)

def analyse_gog_data(gog_data):
    lines_tested = 0
    dir_checked = 0
    dir_prev = ""
    dir_now = ""
    setup_cnt = 0
    patch_cnt = 0
    patch_toggle = False
    patch_counter = 0
    for line in gog_data:
        lines_tested += 1
        dir_now = line['dir']
        if dir_now != dir_prev or dir_prev == "":
            dir_prev = dir_now
            dir_checked += 1
            if setup_cnt > 0:
                if setup_cnt > 1:
                    print "%s has %d SetUp files." % (line['dir'], setup_cnt)
                setup_cnt = 0
            if patch_cnt > 0:
                if patch_cnt > 1:
                    print "%s has %d Patch files." % (line['dir'], patch_cnt)
                patch_cnt = 0
            if patch_toggle:
                print line['dir'], "has been patched"
                patch_toggle = False
                patch_counter += 1
        if re.search(r'.*setup.*\.exe.*$', line['file']):
            setup_cnt += 1                   
            if setup_cnt > 1:
                print "+", line['dir'],"=>", line['file']
        if re.search(r'.*patch.*\.exe.*$', line['file']):
            patch_cnt += 1
            patch_toggle = True
            if patch_cnt > 1:
                print "+", line['dir'],"=>", line['file']
    print
    print "Lines tested =", lines_tested
    print "Directories Checked =", dir_checked
    print "Directories with Patches =", patch_counter
    return(True)

def main():
    gog_data = []
    ok1 = False
    print "Starting..."
    print
    welcome("Py-GOGPurge Version " + str(BS_version) + ", " + str(BS_builddate))
    print "Reading GOG File Tree..."
    if get_filelist():
        print "...OK!"
    else:
        print "...Whoops, we have a problem!"
    print "Loading GOG data from", gog_filespec2
    '''
    print
    (ok1, gog_data) = load_gog_data(gog_filespec2)
    if ok1:
        print
        print len(gog_data),"Directories of GOG data found in %s - OK!" % gog_filespec1
        #print
        counter = 16
        for line in gog_data:
            counter += 1
            if counter >15:
                break
            print line['dir'].lower()
        print
        analyse_gog_data(gog_data)
    else:
        print "GOG data load problem!"
    '''
    print
    print "...Finished!"
    #End

if __name__ == '__main__':
    main()

#EOF
