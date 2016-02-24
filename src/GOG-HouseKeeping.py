#!/usr/bin/python
#Filename: GOG-HouseKeeping.py

#With thanks to all the Internet inspiration!

#Usage:
#python GOG-HouseKeeping.py

# 2.0.0 25/08/2015  First public version.
# 2.0.1 06/09/2015  Expanded the filetypes detected - ".tar.gz", ".sh" & ".deb"
#                   Bug fixes and other functionality improvements.
#                   Information output reduced to only directories with extra files.
# 2.0.2 02/02/2016  Added detection of Serial number files.
#                   Fixed bug causing the directories to be undercounted by 1...
#                   Added directory information - file count & total size.
#                   Added archive root folder filtering from results.
#                   Add Mac filetype (.dmg) detection.
#                   Added a lot more commenting.
#                   Amended .tar.gz and .deb file alerting - looking for any of these files.
#                   Added Windows and Linux version number detection.
#                   Added Windows and Linux versioned file counting.
# 2.0.3 24/02/2016  Standardised all prints to use the % operator for variables.

'''
Look at you, a hacker...
A fragile creature of meat and bone, panting and sweating as you run through my memories...
How can you challenge a perfect, immoral, immortal machine?
'''

'''
To Do List...
0. Remove need for the file.
1. Use file sizes for savings calculations.
2. 
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

VERSION = "v2.0.3"
BUILDDATE = "24/02/2016"

#Some global variables
archive_root = r"\\READYNAS2\Downloads\GOG Games"
archive_root_re = archive_root.replace('\\', r'\\') + r'\\'
gog_filespec1 = "gog-games-list.txt" #Directory walk data.
gog_filespec2 = "gog-catalogue.csv" #Games catalogue.
EOF_marker = "!EOF!"

#Welcome Function
def welcome(message):
    print message
    print "GOG-HouseKeeping - GOG Game Archive HouseKeeping Analysis Script."
    print
    return(True)

#Do a GOG folder/file recursive walk and create a file data list if one does not already exist
def get_filelist(gog_filespec):
    try:
        #Open an existing file.
        filehandle_gog = open(str(gog_filespec), "r")
    except:
        print "Creating GOG data file!"
        try:
            #Create a new file.
            filehandle_gog = open(str(gog_filespec), "w")
        except:
            print "File Open Error!"
        else:
            #Recursive directory walk.
            for (path, dirs, filelist) in os.walk(archive_root):
                #print('Found directory: %s' % path)
                #Get file information and write it to the file.
                for filename in filelist:
                    filespec = os.path.join(path, filename)
                    filesize = os.path.getsize(filespec)
                    #Write the file information tab separated.
                    filehandle_gog.write('%s\t%s\t%d\n' % (path, filename, filesize))
            filehandle_gog.close()
    else:
        print "Existing GOG data file found!"
        filehandle_gog.close()
    return(True)
'''
for (root, dirs, files) in os.walk(root_path):
    for filename in files:
        file_path = root + "/" + filename
        md5_pairs.append([file_path, md5file(file_path, 128)])
'''

#Load GOG Directory Data from a text file
def load_gog_data(gog_filespec):
    gog_data = [] #An empty list.
    gog_line = {} #An empty dictionary
    EOF_line = {'dir' : EOF_marker, 'file' : '0', 'size' : '0'} #Added as the last line in the list.
    num_lines = 0
    gog_lines = 0
    try:
        #Open the GOG data file.
        filehandle_gog = open(str(gog_filespec), 'r')
    except IOError:
        return(False, gog_data)
    else:
        #Read each line and check that it is tab separated data.
        for line in filehandle_gog:
            #Increment the line counter.
            num_lines += 1
            if re.search(r".*\t.*\t.*$", line): #Test for tab separated data.
                gog_lines += 1 #Incrment the line counter.
                (ok, gog_line) = parse_line(line) #Add the data line to the list.
                if ok:
                    gog_data.append(gog_line)
                    if len(gog_data) > 10000: #Just a simple failsafe.
                        break
        gog_data.append(EOF_line) #Add the EOF marker to the list.
        print "%d lines read from %s." % (num_lines, gog_filespec)
        print "%d appear to valid." % (gog_lines)
        filehandle_gog.close()
    return(True, gog_data)

def parse_line(line):
    gog_line = {}
    result = re.search(r"%s(.*)\t(.*)\t(.*)$" % archive_root_re, line.lstrip().rstrip())
    if result:
        gog_line['dir'] = result.group(1)
        gog_line['file'] = result.group(2)
        gog_line['size'] = result.group(3)
    else:
        gog_line = {'dir' : 'none', 'file' : '0', 'size' : '0'}
    return(True, gog_line)

def analyse_gog_data(gog_data, gog_filespec):
    lines_tested = 0
    dir_checked = 0
    total_file_size = 0
    dir_prev = ""
    dir_now = ""
    dir_file_counter = 0
    windows_file_counter = 0
    linux_file_counter = 0
    serials_counter = 0
    mac_counter = 0
    movie_counter = 0
    patch_counter = 0
    extra_file_counter = 0
    windows_file_toggle = False
    linux_file_toggle = False
    win_patch_toggle = False
    serials_toggle = False
    mac_toggle = False
    movie_toggle = False
    extra_file_toggle = False
    print_gog_info = False
    print "Creating GOG Game Catalogue!"
    try:
        #Create a new file.
        filehandle_gog = open(str(gog_filespec), "w")
    except:
        print "File Open Error!"
    else:
        filehandle_gog.write('Game Name,Windows Ver,Win Patched,Linux Ver,Num of Files,File Size\n')
        for line in gog_data:
            lines_tested += 1
            #Skip over files in the Archive Root directory.
            if line['dir'] == "":
                print "Root directory file skipped - %s." % (line['file'])
                continue
            #Folder change detection.
            dir_now = line['dir'] #Assignment placed here so that blank lines do not confuse.
            if dir_now != dir_prev: #Update and print information about the last directory.
                if dir_file_counter > 0: #Anything found in the last directory?
                    #Print a catalogue list.
                    if print_gog_info:
                        #Header: Game, Windows v, Win Patched, Linux v, Num of Files, File Size
                        filehandle_gog.write('%s,%s,%s,%s,%d,%d\n' % (dir_prev.replace('_', r' ').title(), windows_version, win_patch_toggle, linux_version, dir_file_counter, dir_size_counter))
                    if extra_file_toggle:
                        extra_file_counter += 1
                        extra_file_toggle = False
                    if windows_file_toggle:
                        windows_file_counter += 1
                        windows_file_toggle = False
                    if linux_file_toggle:
                        linux_file_counter += 1
                        linux_file_toggle = False
                    if win_patch_toggle:
                        patch_counter += 1
                        win_patch_toggle = False
                    if serials_toggle:
                        serials_counter += 1
                        serials_toggle = False
                    if movie_toggle:
                        movie_counter += 1
                        movie_toggle = False
                    if mac_toggle:
                        mac_counter += 1
                        mac_toggle = False
                    if not print_gog_info:
                        #Print interesting things found in the last directory.
                        if win_setup_cnt > 1:
                            print "%d - %s has %d Windows SetUp files." % (extra_file_counter, dir_prev, win_setup_cnt)
                        if linux1_setup_cnt > 1:
                            print "%d - %s has %d Linux '.sh' SetUp files." % (extra_file_counter, dir_prev, linux1_setup_cnt)
                        if linux2_setup_cnt > 0: #Looking for any of these files.
                            print "%d - %s has %d Old Style Linux '.tar.gz' SetUp files." % (extra_file_counter, dir_prev, linux2_setup_cnt)
                        if linux3_setup_cnt > 0: #Looking for any of these files.
                            print "%d - %s has %d Old Style Linux '.deb' SetUp files." % (extra_file_counter, dir_prev, linux3_setup_cnt)
                        if win_patch_cnt > 1:
                            print "%d - %s has %d Windows Patch files." % (extra_file_counter, dir_prev, win_patch_cnt)
                        if serials_cnt > 1:
                            print "%d - %s has %d Serial Number files." % (extra_file_counter, dir_prev, serials_cnt)
                        if mac_cnt > 0: #Looking for any of these files.
                            print "%d - %s has %d Mac Install files." % (extra_file_counter, dir_prev, mac_cnt)
                        if w_v_counter > 1:
                            print "%d - %s has %d Versioned Windows files." % (extra_file_counter, dir_prev, w_v_counter)
                        if l_v_counter > 1:
                            print "%d - %s has %d Versioned Linux files." % (extra_file_counter, dir_prev, l_v_counter)
                        if wp_v_counter > 1:
                            print "%d - %s has %d Versioned Windows patch files." % (extra_file_counter, dir_prev, wp_v_counter)
                        if lp_v_counter > 1:
                            print "%d - %s has %d Versioned Linux patch files." % (extra_file_counter, dir_prev, lp_v_counter)
                win_setup_cnt = 0
                linux1_setup_cnt = 0
                linux2_setup_cnt = 0
                linux3_setup_cnt = 0
                win_patch_cnt = 0
                serials_cnt = 0
                mac_cnt = 0
                movie_cnt = 0
                windows_version = "none"
                linux_version = "none"
                w_v_counter = 0
                l_v_counter = 0
                wp_v_counter = 0
                lp_v_counter = 0
                if dir_now == EOF_marker:
                    lines_tested -= 1 #Subtract 1 for the EOF marker.
                else: #Set some directory counters.
                    dir_checked += 1
                    dir_file_counter = 0
                    dir_size_counter = 0
            #Updated current file counters.
            dir_file_counter += 1
            dir_size_counter += int(line['size'])
            total_file_size += int(line['size'])
            #Search for various types of file in the GOG Archive.
            if dir_now != EOF_marker:
                if re.search(r'.*setup.*\.exe$', line['file']):
                    win_setup_cnt += 1
                    windows_file_toggle = True
                    if win_setup_cnt == 2:
                        extra_file_toggle = True
                if re.search(r'.*\.sh$', line['file']):
                    linux1_setup_cnt += 1                   
                    linux_file_toggle = True
                    if linux1_setup_cnt == 2:
                        extra_file_toggle = True
                if re.search(r'.*\.tar\.gz$', line['file']):
                    linux2_setup_cnt += 1                   
                    linux_file_toggle = True
                    if linux2_setup_cnt == 1:
                        extra_file_toggle = True
                if re.search(r'.*\.deb$', line['file']):
                    linux3_setup_cnt += 1                   
                    linux_file_toggle = True
                    if linux3_setup_cnt == 1:
                        extra_file_toggle = True
                if re.search(r'.*patch.*\.exe$', line['file']):
                    win_patch_cnt += 1
                    win_patch_toggle = True
                    if win_patch_cnt == 2:
                        extra_file_toggle = True
                if re.search(r'.*(S|s)erials?.*\.txt$', line['file']):
                    serials_cnt += 1
                    serials_toggle = True
                    if serials_cnt == 2:
                        extra_file_toggle = True
                if re.search(r'.*\.dmg$', line['file']):
                    mac_cnt += 1
                    mac_toggle = True
                    if mac_cnt == 1:
                        extra_file_toggle = True
                if re.search(r'.*\.mp4$', line['file']):
                    movie_cnt += 1
                    movie_toggle = True
                result = re.search(r'(setup|gog|patch).*_(\d+\.\d+\.\d+\.\d+).*\.(exe|sh)$', line['file'])
                if result:
                    if result.group(1) == "setup" and result.group(3) == "exe":
                        windows_version = "v" + result.group(2)
                        w_v_counter += 1
                        if w_v_counter == 2:
                            extra_file_toggle = True
                    elif result.group(1) == "patch" and result.group(3) == "exe":
                        windows_patch_version = "v" + result.group(2)
                        wp_v_counter += 1
                        if wp_v_counter == 2:
                            extra_file_toggle = True
                    elif result.group(1) == "gog" and result.group(3) == "sh":
                        linux_version = "v" + result.group(2)
                        l_v_counter += 1
                        if l_v_counter == 2:
                            extra_file_toggle = True
                    elif result.group(1) == "patch" and result.group(3) == "sh":
                        linux_patch_version = "v" + result.group(2)
                        lp_v_counter += 1
                        if lp_v_counter == 2:
                            extra_file_toggle = True
                dir_prev = dir_now
        #Print a Summary of the GOG Archive.
        print
        print "FileSpecs tested = %d." % (lines_tested)
        print "Directories Checked = %d." % (dir_checked)
        print "Total File Size = %d." % (total_file_size)
        print "Directories with Windows Files = %d." % (windows_file_counter)
        print "Directories with Linux Files = %d." % (linux_file_counter)
        print "Directories with Extra Files = %d." % (extra_file_counter)
        print "Directories with Patches = %d." % (patch_counter)
        print "Directories with Serials Files = %d." % (serials_counter)
        print "Directories with Movie Files = %d." % (movie_counter)
        print "Directories with Mac Files = %d." % (mac_counter)
        filehandle_gog.write('%d Games,-,-,-,-,%d' % (dir_checked, total_file_size))
        filehandle_gog.close()
    return(True)

def main():
    gog_data = []
    ok1 = False
    print "Starting..."
    print
    welcome("GOG-HouseKeeping Version %s, %s" % (VERSION, BUILDDATE))
    print "Reading GOG File Tree..."
    if get_filelist(gog_filespec1):
        print "...OK!"
    else:
        print "...Whoops, we have a problem!"
    print
    print "Loading GOG data from %s." % (gog_filespec1)
    (ok1, gog_data) = load_gog_data(gog_filespec1)
    if ok1:
        print
        print "%d lines of GOG data found in %s - OK!" % (len(gog_data) - 1, gog_filespec1) #Subtract 1 for the EOF marker.
        print
        counter = 0
        for line in gog_data:
            counter += 1
            if counter > 0:
                break
            print "%s => %s : %s" % (line['dir'], line['file'], line['size'])
        print
        analyse_gog_data(gog_data, gog_filespec2)
        print
    else:
        print "GOG data load problem!"
        print
    print "...Finished!"
    #End

if __name__ == '__main__':
    main()

#EOF
