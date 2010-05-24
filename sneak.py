#!/usr/bin/env python
BASE_URL="http://localhost:8083/"

gkey = ""
username = None
password = None
def usage():
    print "sneakernet 0.1"
    print "format"
    
def ask_authenticate():
    global username,password
    if username!=None:
        return (username,password)
    print "Username: ",
    username = raw_input()
    import getpass
    password = getpass.getpass()
    return (username,password)
def post(url,values):
    import urllib
    import urllib2
    real_url = BASE_URL + url
    data = urllib.urlencode(values)
    req = urllib2.Request(real_url,data)
    response = urllib2.urlopen(req)
    return response.read()
    
class fileOrDirectoryDialog:
    def __init__(self,parent):
        from Tkinter import Toplevel, Label, Button

        top = self.top = Toplevel(parent)

        

def interactive_format():
    diskname = raw_input("Disk name? ")
    print "Are you sure you want to format %s? y/N" % diskname
    if raw_input()!="y": return
    print "Pick a new name: ",
    newname = raw_input()
    import sys
    print "Formatting disk %s" % diskname
    if sys.platform=="darwin":
        import os
        os.system("diskutil eraseVolume \"MS-DOS FAT32\" %s '%s'" % (newname,diskname))
        mounted_path = "/Volumes/%s" % newname
    else:
        print "Unsupported platform."
    import os
    sneakdir = os.path.join(mounted_path,".sneak")
    os.mkdir(sneakdir)
    
    file = open(os.path.join(sneakdir,"CACHENAME"),"w")
    file.write(newname)
    file.close()
    import statvfs
    stat = os.statvfs(mounted_path)
    freespace = stat[statvfs.F_BFREE] * stat[statvfs.F_FRSIZE]
    (username,password) = ask_authenticate()
    print "Should this be intern or extern?  I/E"
    ie = raw_input()
    if ie=="I":
        type="INTERN"
    elif ie=="E":
        type="EXTERN"
    else:
        raise Exception("Invalid type")
    print "Give me a key of a CacheLocation of where to put it: "
    loc = raw_input()
    result = post("teamadmin/format",{"username":username,"password":password,"type":type,"freespace":freespace,"name":newname,"location":loc})
    if result != "OK":
        raise Exception("Something went wrong.")
def sneak_dir_for_disk(path):
    from os.path import exists
    import os.path
    if exists(os.path.join(path,".sneak")):
        return sneak_dir_for_disk(os.path.join(path,".sneak"))
    return exists(os.path.join(path,"CACHENAME")) and path or None
def canonical_name(path):
    from os.path import exists
    import os
    if exists(os.path.join(path,".sneak")):
        return canonical_name(os.path.join(path,".sneak"))
    if exists(os.path.join(path,"CACHENAME")):
        sneakfile = open(os.path.join(path,"CACHENAME"))
        s = sneakfile.read()
        sneakfile.close()
        return s
    return None
def is_disk(name,path):
    print "Checking to see if %s is %s" % (path,name)
    if canonical_name(path)==name: return True
    return False
def get_cache_directory():
    import os.path
    path = os.path.expanduser("~/.sneak/") #on some other OS, do something else?
    import os
    if not os.path.exists(path): #if it doesn't exist, make it
        os.mkdir(path)
        sneakfile = open(os.path.join(path,"CACHENAME"),"w")
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        key = ""
        from random import choice
        for i in range(0,16):
            key += choice(chars)
        sneakfile.write(key)
        sneakfile.close()
    return path
def all_caches():
    import sys
    result = []
    if sys.platform=="darwin":
        import os
        disks = os.listdir("/Volumes/")
        for disk in disks:
            disk = os.path.join("/Volumes",disk)
            if os.path.ismount(disk):
                paths = sneak_dir_for_disk(disk)
                if paths is not None: result.append(paths)

    elif sys.platform=="win32":
        import os
        drives = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for drive in drives:
            if os.path.exists(drive+":\\"):
                paths = sneak_dir_for_disk(drive+":\\")
                if paths is not None:
                    result.append(paths)
    else:
        raise Exception("Unsupported platform.")
        
    paths = sneak_dir_for_disk(get_cache_directory())
    if paths is not None: result.append(paths)
    return result
            
        
def find_cache(name):
    paths = all_caches()
    for path in paths:
        if is_disk(name,path): return path
    return None
"""
    import sys
    if sys.platform=="darwin":
        import os
        disks = os.listdir("/Volumes/")
        for disk in disks:
            disk = os.path.join("/Volumes",disk)
            if os.path.ismount(disk):
                if is_disk(name,disk): return disk
        if is_disk(name,get_cache_directory()): return get_cache_directory()
    else:
        raise Exception("Not implemented")"""

    

def tar (what, tf):
    import tarfile
    tar = tarfile.open(tf,"w:bz2")
    import os
    tar.add(what,arcname=os.path.basename(what))
    #print os.path.basename(what)
    tar.close()
def untar(tf,where):
    import tarfile
    tar = tarfile.open(tf,"r:bz2")
    tar.extractall(path=where)
    tar.close()
def encrypt(file,key):
    import subprocess
    import os.path
    import sys
    if sys.platform=="darwin":
        bcrypt_executable = os.path.join(sys.path[0],"bcrypt") #windows will require some hackage
    elif sys.platform=="win32":
        bcrypt_executable = os.path.join(sys.path[0],"bcrypt.exe")
    else:
        raise Exception("Unsupported platform")
    p = subprocess.Popen([bcrypt_executable,"-rc",file],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    p.communicate("%s\n%s\n"%(key,key))
    p.wait()
def decrypt(file,key):
    import subprocess
    if not file.endswith(".bfe"): raise Exception("Won't decrypt right")
    print "bcrypt_decrypt: %s" % file
    if sys.platform=="darwin":
        bcrypt_executable = os.path.join(sys.path[0],"bcrypt")
    elif sys.platform=="win32":
        bcrypt_executable = os.path.join(sys.path[0],"bcrypt.exe")
    p = subprocess.Popen([bcrypt_executable,file],stdin=subprocess.PIPE)
    p.communicate("%s\n" % key)
    p.wait()
def upload_folder():
    global gkey
    from tkFileDialog import askdirectory
    file = askdirectory()
    root.quit()
    root.destroy()
    complete_upload(file)

def get(url,values):
    import urllib
    import urllib2
    real_url = BASE_URL+url+"?" + urllib.urlencode(values)
    req = urllib2.Request(real_url)
    response = urllib2.urlopen(req)
    return response.read()

def sync_cache(path):
    import os
    files = os.listdir(path)
    cname = open(os.path.join(path,"CACHENAME")).read()
    print "Syncing %s" % cname
    (username,password) = ask_authenticate()
    supposedly_files = get("cache/sync",{"username":username,"password":password,"cache":cname})
    print supposedly_files
    if not supposedly_files.startswith("OK"):
        raise Exception("Sync repsonse wasn't what I expected: %s" % supposedly_files)
    deletes = []
    adds = []
    #see what files need to be deleted
    supposedly_files = supposedly_files.split("\n")[1:]
    for file in supposedly_files:
        if file=="":continue
        if file+".tar.bfe" not in files:
            deletes += [file]
    for file in files:
        #chomp .tar.bfe
        if file=="CACHENAME": continue
        if file=="._.Trashes": continue #mac osx makes this file
        if file==".Trashes": continue
        if file==".DS_Store": continue
        if not file.endswith(".tar.bfe"):
            raise Exception("What is this file doing here: %s?" % file)
        shortname = "".join(file[0:len(file)-8])
        if shortname not in supposedly_files:
            adds += [shortname]
    addstr = ""
    delstr = ""
    for file in adds:
        print "Adding %s" % file
        addstr += "\n" + file
    for file in deletes:
        print "Deleting %s" % file
        delstr += "\n" + file
        
    #compute free size
    if sys.platform=="darwin":
        import statvfs
        stat = os.statvfs(path)
        size=str(stat[statvfs.F_BFREE] * stat[statvfs.F_FRSIZE])
    elif sys.platform=="win32":
        import ctypes

        free_bytes = ctypes.c_ulonglong(0)

        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
        size = str(free_bytes.value)
    else:
        raise Exception("Unsupported platform.")
    post("cache/sync",{"username":username,"password":password,"cache":cname,"adds":addstr,"deletes":delstr,"size":size})
        
def sync_all_disks():
    disks = all_caches()
    for disk in disks:
        sync_cache(disk)

def complete_upload(file):
    global gkey
    import os.path
    tarfilename = os.path.join(get_cache_directory(),gkey+".tar")
    print "Compressing data... (this may take a few minutes)"
    tar(file,tarfilename)

    readfile = open(tarfilename,"rb")
    part = 0
    print "splitting into 500mb chunks"
    def supercopy(to,fromfile):
        writefile = open(to,"wb")
        mb_copied=0
        while True:
            data = fromfile.read(1024*1024)
            if len(data)==0:
                print "Done splitting (final)..."
                writefile.close()
                return True
            writefile.write(data)
            mb_copied += 1
            if mb_copied==500:
                print "Print done splitting (falsereturn)"
                writefile.close()
                return False
    while True:
        writefile = tarfilename + "."+str(part)
        result = supercopy(writefile,readfile)
        print "Finished writing " + tarfilename + "." + str(part)
        part += 1
        if result:
            break
        #writefile = open(tarfilename + "." + str(part),"w")
    readfile.close()
    os.unlink(tarfilename)

        
        
        
        
    from random import choice
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    key = ""
    for i in range(0,32):
        key += choice(chars)
    print "Encrypting data... (%s)" % key
    for i in range(0,part):
        print "encrypting part %s" % i
        encrypt(tarfilename + "." + str(i),key)
        os.remove(tarfilename + "." + str(i))
    #recombine files
    outfile = tarfilename + ".bfe"
    out = open(outfile,"wb")
    out.write("ARCHIVE_FORMAT_V2")

    for i in range(0,part):
        infile = open(tarfilename+"."+str(i)+".bfe","rb")
        size = os.path.getsize(tarfilename+"."+str(i)+".bfe")
        out.write(str(size)+"\n")
        while True:
            #low memory implementation for malcolm
            data = infile.read(1024*1024) #1mb buffer
            if len(data)==0: break
            out.write(data)
        infile.close()
        os.unlink(tarfilename+"."+str(i)+".bfe")
    size = os.path.getsize(tarfilename+".bfe")
    (username,password) = ask_authenticate()
    result = post("share/uploadcomplete",{"username":username,"password":password,"key":key,"size":str(size),"id":gkey})
    if not result.startswith("OK"):
        print result
        raise Exception("That didn't work.  See above.")
    sync_cache(get_cache_directory())
def upload_file():

    global gkey
    from tkFileDialog import askopenfilename
    file = askopenfilename()
    root.quit()
    root.destroy()
    complete_upload(file)
    
def decrypt_file(cache,fileid,key):
    cache = find_cache(cache)
    from Tkinter import Tk
    root = Tk()
    from tkFileDialog import askdirectory
    if sys.platform=="darwin":
        from os import system
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    print "Have a look at the dialog..."
    extract_where = askdirectory()

    root.destroy()
    import shutil
    dest = os.path.join(extract_where,fileid)
    print cache
    shutil.copyfile(os.path.join(cache,fileid+".tar.bfe"),dest+".tar.bfe")
    test = open(dest + ".tar.bfe","rb")
    data = test.read(17)
    def super_split(infile,destname,size):
        writefile = open(destname + ".temp.tar.bfe","wb")
        BYTES_LEFT = size
        while True:
            data = infile.read(min(BYTES_LEFT,1024*1024))
            BYTES_LEFT -= len(data)
            writefile.write(data)
            if BYTES_LEFT==0:
                break
        writefile.close()
    def super_combine(src,final):
        srcfile = open(src+".temp.tar","rb")
        while True:
            data = srcfile.read(1024*1024)
            if len(data)==0:
                break
            final.write(data)
        srcfile.close()
            
    if data=="ARCHIVE_FORMAT_V2":
        final_tar = dest+".tar"
        final = open(final_tar,"wb")
        while True:
            sizestr = test.readline().strip()
            if len(sizestr)==0: break
            size = int(sizestr)
            super_split(test,dest,size)
            decrypt(dest+".temp.tar.bfe",key)
            super_combine(dest,final)
            os.unlink(dest+".temp.tar")
        test.close()
        os.unlink(dest+".tar.bfe")
        final.close()
    else:    #format V1
        decrypt(dest+".tar.bfe",key)
    #os.remove(dest+".tar.bfe") #looks like bcrypt removes this
    untar(dest+".tar",extract_where)
    os.remove(dest+".tar")

def upload(key):
    global gkey, root
    gkey = key
    from Tkinter import Tk
    root = Tk()
    #d = fileOrDirectoryDialog(root)
    from Tkinter import Label, Button
    Label(root,text="What do you want to share?").pack()
    Button(root,text="Share one file",command=upload_file).pack(pady=5)
    Button(root,text="Share whole folder",command=upload_folder).pack(pady=5)
    import sys
    if sys.platform=="darwin":
        from os import system
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    print "Have a look at the dialog..."

    root.mainloop()
    
def try_move_to(file_id,destination_path):
    import shutil
    search_paths = all_caches()
    import os.path
    for search_path in search_paths:
        filename = os.path.join(search_path,file_id)+".tar.bfe"
        if os.path.exists(filename):
            print "Got %s!  Moving to %s" % (filename,destination_path)
            try:
                shutil.copy(filename,os.path.join(destination_path,file_id+".tar.bfe"))
            except:
                print "Copy failed (probably out of space).  Moving on..."
                os.unlink(os.path.join(destination_path,file_id+".tar.bfe"))
            return

            
def do_run_script():
    #Let's make sure everything's up-to-date before we begin
    sync_all_disks()
    disks = all_caches()
    diskstr = ""
    (username,password) = ask_authenticate()
    for disk in disks:
        name = canonical_name(disk)
        diskstr += name + "\n"
    data = post("run/MoveTo",{"username":username,"password":password,"disks":diskstr})
    if not data.startswith("OK"):
        print data
        raise Exception("Error ocurred.")
    disk_strs = data.split("\n")
    for disk in disk_strs[1:]:
        disk = disk.strip()
        if disk=="": continue #ignore trailing newline
        file_part = disk.split(":")
        disk = file_part[0]
        file_part = file_part[1]
        files = file_part.split("|")
        print "Considering disk %s" % disk
        for file in files:
            if file=="": continue
            print "Considering file %s" % file
            try_move_to(file,sneak_dir_for_disk(find_cache(disk)))
            
        
    
    
    
def purge_pass():
    disks = all_caches()
    again_again = False
    for disk in disks:
        files = os.listdir(disk)
        for file in files:
            #chomp .tar.bfe
            if file=="CACHENAME": continue
            if file=="._.Trashes": continue #mac osx makes this file
            if file==".Trashes": continue
            if file ==".DS_Store": continue
            if not file.endswith(".tar.bfe"):
                raise Exception("What is this file doing here: %s?" % file)
            shortname = "".join(file[0:len(file)-8])
            (username,password) = ask_authenticate()
            print "Purge %s?" % shortname,
            try:
                result = get("purge",{"username":username,"password":password,"cache":canonical_name(disk),"content":shortname})
            except:
                result = "FAILED"
            print result
            import shutil
            if result=="MOVE_TO_SOFTCACHE":
                softcache = get_cache_directory()
                if not os.path.exists(os.path.join(softcache,shortname+".tar.bfe")):
                    shutil.move(os.path.join(disk,shortname+".tar.bfe"),os.path.join(softcache,shortname+".tar.bfe"))
                    again_again=True
            elif result=="PURGE_AT_WILL":
                os.unlink(os.path.join(disk,shortname+".tar.bfe"))
                again_again = True
    return again_again
def do_file(filename):
   print "Reading file %s" % filename
   file = open(filename)
   contents = file.read()
   file.close()
   lines = contents.split("\n")
   if lines[0]!="SNEAK10":
    raise Exception("Invalid file header (maybe you're using an old version of the software?)")
   if lines[1]=="UPLOAD":
    upload(lines[2])
   elif lines[1]=="DECRYPT":
    decrypt_file(cache=lines[2],fileid=lines[3],key=lines[4])
   elif lines[1]=="RUN":
        do_run_script()
    
   else:
    raise Exception("Unknown verb.")
    
if __name__=="__main__": #pyongyang imports to compile to pyo
    import os.path
    import sys
    if len(sys.argv)>1:    
        if sys.argv[1]=="format":
            interactive_format()
        else:
            do_file(sys.argv[1])
    sync_all_disks()
    if purge_pass():
        sync_all_disks()


