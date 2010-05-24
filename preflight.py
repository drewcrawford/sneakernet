#!/usr/bin/env python
BASE_URL="http://localhost:8083/"

# Imports
import os
import sys
import urllib2
import zipfile
dest_path = "c:\\Program Files\\Sneakernet"
fileTypeName = "sneakernetFile"
def PullFile(url, file, writeType, fileName):
   f = urllib2.urlopen(url, file)
   downloadedFile = open(fileName, writeType)
   size = int(f.info()["content-length"])
   completed = 0;
   while completed < size:
       data = f.read(100)
       completed += 100
       downloadedFile.write(data)
   downloadedFile.close()
   del f
   return "Download Complete!"

# Check python install:
if not os.path.exists("c:\\python26"):
   print "Looks like Python's not installed.  Downloading... (may take some time)"
   print PullFile("http://www.python.org/ftp/python/2.6/python-2.6.msi", "python-2.6.msi", "wb", "python-installer.msi")    
   os.system("python-installer.msi /q")

# Pull Software
print PullFile(BASE_URL+"sneakernet-win.zip", "sneakernet-win.zip", "wb", "something.zip")
zfobj = zipfile.ZipFile("something.zip")
zfobj.extractall(dest_path)

#Set File Associations
fileAssociations = {".sneak":"run-sneakernet.bat"} # dictionary for multiple associations?
for fileType in fileAssociations.keys():
   os.system("assoc " + fileType + "=" + fileTypeName)
   assocstr = "ftype " + fileTypeName + '=' + '"' + dest_path + "\\" + fileAssociations[fileType] + '"' + ' "%1"'
   print assocstr
   os.system(assocstr)

print "Install completed successfully!"
raw_input()


'''
def unzipFileToDir(file, dir):
   os.mkdir(dir, 0777)
   zfobj = zipfile.ZipFile(file)
   for name in zfobj.namelist():
       if name.endswith('/'):
           os.mkdir(os.path.join(dir, name))
       else:
           outfile = open(os.path.join(dir, name), 'wb')
           outfile.write(zfobj.read(name))
           outfile.close()
'''