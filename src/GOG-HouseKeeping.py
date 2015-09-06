#!/usr/bin/python
#Filename: GOG-HouseKeeping.py

#With thanks to all the Internet inspiration!

#Usage:
#python GOG-HouseKeeping.py

# 2.0.0 25/08/2015  First public version.
# 2.0.1 06/09/2015  Expanded the filetypes detected - ".tar.gz", ".sh" & ".deb"
#                   Bug fixes and other functionality improvements.
#                   Information output reduced to only directories with extra files.

'''
Look at you, a hacker...
A fragile creature of meat and bone, panting and sweating as you run through my memories...
How can you challenge a perfect, immoral, immortal machine?
'''

'''
To Do List...
0. Remove need for the file.
1. Use file sizes for savings calculations.
2. Commenting required!
3. 
4. 
5. 
6. 
7. 
8. 
9. Publish on GitHub.
'''

import os
import re

BS_version = "v2.0.1"
BS_builddate = "06/09/2015"

#Some global variables
gog_filespec = "gog-games-list.txt"

#Welcome Function
def welcome(message):
    print message
    print "GOG-HouseKeeping - GOG Game Archive HouseKeeping Analysis Script."
    print
    return(True)

#Do a GOG folder/file recursive walk and create a file data list
def get_filelist():
    #Set the directory where you want to start.
    root = r"\\READYNAS2\Downloads\GOG Games"
    try:
        filehandle_gog = open(str(gog_filespec), "w")
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

#Load GOG Directory Data from a text file
def load_gog_data(filespec):
    gog_data = []
    gog_line = {}
    num_lines = 0
    gog_lines = 0
    try:
        filehandle_gog = open(str(gog_filespec), 'rb')
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
    linux1_setup_cnt = 0
    linux2_setup_cnt = 0
    linux3_setup_cnt = 0
    windows_file_counter = 0
    linux_file_counter = 0
    patch_counter = 0
    extra_file_counter = 0
    windows_file_toggle = False
    linux_file_toggle = False
    patch_toggle = False
    extra_file_toggle = False
    console_o_p = False
    for line in gog_data:
        lines_tested += 1
        dir_now = line['dir']
        if dir_now != dir_prev or dir_prev == "":
            dir_checked += 1
            if extra_file_toggle:
                extra_file_counter += 1
                extra_file_toggle = False
            if setup_cnt > 0:
                if setup_cnt > 1:
                    console_o_p = True
                    print "%d - %s has %d Windows SetUp files." % (extra_file_counter, dir_prev, setup_cnt)
                setup_cnt = 0
            if linux1_setup_cnt > 0:
                if linux1_setup_cnt > 1:
                    console_o_p = True
                    print "%d - %s has %d Linux '.tar.gz' SetUp files." % (extra_file_counter, dir_prev, linux1_setup_cnt)
                linux1_setup_cnt = 0
            if linux2_setup_cnt > 0:
                if linux2_setup_cnt > 1:
                    console_o_p = True
                    print "%d - %s has %d Linux '.sh' SetUp files." % (extra_file_counter, dir_prev, linux2_setup_cnt)
                linux2_setup_cnt = 0
            if linux3_setup_cnt > 0:
                if linux3_setup_cnt > 1:
                    console_o_p = True
                    print "%d - %s has %d Linux '.deb' SetUp files." % (extra_file_counter, dir_prev, linux3_setup_cnt)
                linux3_setup_cnt = 0
            if patch_cnt > 0:
                if patch_cnt > 1:
                    console_o_p = True
                    print "%d - %s has %d Windows Patch files." % (extra_file_counter, dir_prev, patch_cnt)
                patch_cnt = 0
            if windows_file_toggle:
                windows_file_counter += 1
                windows_file_toggle = False
            if linux_file_toggle:
                linux_file_counter += 1
                linus_file_toggle = False
            if patch_toggle:
                patch_counter += 1
                patch_toggle = False
            if console_o_p:
                print
                console_o_p = False
            dir_prev = dir_now
        if re.search(r'.*setup.*\.exe$', line['file']):
            setup_cnt += 1
            windows_file_toggle = True
            if setup_cnt == 2:
                extra_file_toggle = True
        if re.search(r'.*gog.*\.tar\.gz$', line['file']):
            linux1_setup_cnt += 1                   
            linux_file_toggle = True
            if linux1_setup_cnt == 2:
                extra_file_toggle = True
        if re.search(r'.*gog.*\.sh$', line['file']):
            linux2_setup_cnt += 1                   
            linux_file_toggle = True
            if linux2_setup_cnt == 2:
                extra_file_toggle = True
        if re.search(r'.*gog.*\.deb$', line['file']):
            linux3_setup_cnt += 1                   
            linux_file_toggle = True
            if linux3_setup_cnt == 2:
                extra_file_toggle = True
        if re.search(r'.*patch.*\.exe$', line['file']):
            patch_cnt += 1
            patch_toggle = True
            if patch_cnt == 2:
                extra_file_toggle = True
    print "Lines tested =", lines_tested
    print "Directories Checked =", dir_checked
    print "Directories with Windows Files =", windows_file_counter
    print "Directories with Linux Files =", linux_file_counter
    print "Directories with Extra Files =", extra_file_counter
    print "Directories with Patches =", patch_counter
    return(True)

def main():
    gog_data = []
    ok1 = False
    print "Starting..."
    print
    welcome("GOG-HouseKeeping Version " + str(BS_version) + ", " + str(BS_builddate))
    print "Reading GOG File Tree..."
    if get_filelist():
        print "...OK!"
    else:
        print "...Whoops, we have a problem!"
    print
    print "Loading GOG data from", gog_filespec
    (ok1, gog_data) = load_gog_data(gog_filespec)
    if ok1:
        print
        print len(gog_data),"Lines of GOG data found in %s - OK!" % gog_filespec
        print
        '''
        counter = 0
        for line in gog_data:
            counter += 1
            if counter >15:
                break
            print line['dir'],"=>", line['file'],":",line['size']
        print
        '''
        analyse_gog_data(gog_data)
        print
    else:
        print "GOG data load problem!"
        print
    print "...Finished!"
    #End

if __name__ == '__main__':
    main()

#EOF
