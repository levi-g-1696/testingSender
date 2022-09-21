

import os.path, os
from ftplib import FTP, error_perm
from shutil import copy2
import csv
from collections import namedtuple

from FoldersCheckLib import  CheckTempFolderStatus
from  lib2 import confreader,copyFilesToArc,Remove1File,RemoveFilesFrom, removeOld,copyFilesFromList
import logging
import time, ftplib, glob
from lib3 import sendFolderFiles,CreateArcFolders,CopyAllFolders,NewPrepareTempFolders,RemoveEmptyFolders,getOnlineGMTTime
import subprocess


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def CreateTestFile(upfolders):
    for foldername  in upfolders:
      folderStrArr= foldername.split("\\")
      lastFArrMember= folderStrArr[ len(folderStrArr)-1]
      timenownum=getOnlineGMTTime("unixtimesec")
      filename="tst"+lastFArrMember+ "-" + str(timenownum)+".csv"

      timenow= getOnlineGMTTime("datetime")
      fileText= f"CreationTime,TestMonitor\r\n{timenow},10"
      fileFullpath= os.path.join(foldername, filename)
   #   f = open(fileFullpath, "x")
      f = open(fileFullpath, "w")
      f.write(fileText)
      f.close()

    return
#-------------------------------------------------------------

def AddToExceptIParr(n,value, ftpExceptIParr ):
    l= list( ftpExceptIParr)   #  WHAT?

    num = n -l.count(value)
    for i in range(1,num):
        ftpExceptIParr.append(value)
    return ftpExceptIParr
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def GetFileNumOnTempFolders (configProps):   # zaglushka
  foldersStat = namedtuple("foldersStat", "tempFolder num")  # a tuple (tempfoldr-path, files-number-in-it)
  resarr = []
  res= resarr.append( foldersStat ("c:\\ccc\\cccc",57))
  res = resarr.append(foldersStat("c:\\cc\\bbbb", 157))
  res = resarr.append(foldersStat("c:\\ccc\\dddd", 0))
  return (res)
#---------------------------------------------------------------------



################################## ###########################3
# def PrepareTempFolders(config):
#     tempfolder=[]
#     for i in range(len(config.sourcefolders)):
#
#         tempfolderStr= temproot+"\\Tmp"+  "-" + config.users[i]+"-"+config.hosts[i]+"-"+ config.ports[i]
#         new_directory(tempfolderStr)
#         tempfolder.append(tempfolderStr)
#         source = config.sourcefolders[i]
#         dest = tempfolder[i]
#         copyFilesToArc(source, dest)
#     return tempfolder




    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

#======================================================

def multisenderSession():
    ## stoping option  ##
    st = "c:\\ftpTransfer\\stop.conf"


    configFile = ".\\transferConfig22.csv"
    log = ".\\Log\\transferLog.csv"
    uproot=".\\Upfolders"
    temproot = ".\\Temp"
    arcroot=  ".\\Arc"
    logoldpath = ".\\LogOld\\"
    ftpExceptIParr = []
    arcFileNameHead="Arc"

    ftpExceptEscapecount = 30
   # st = "c:\\ftpTransfer\\stop.conf"

    session = namedtuple("session", "ip port user psw sourcefolder")
    config= namedtuple ("config","hosts ports users passwords sourcefolders")
    foldersStat= namedtuple("foldersStat","tempFolder num") #a tuple (tempfoldr-path, files-number-in-it)
    fileNumberLimitforAlert=150
#--------------------------------


    ######################
    f1 = open(log, "r")
    logfileid = f1.fileno
    f1.close
    ###################
    print()
    print("    ftp transfer is started\r\n")
    count1m = 0
    count3m = 0
    count60m = 0

#-----------

#=====================================

    isEnable,isLastDest, users, passw, upfolder,  destinationHOST, port = confreader(configFile)
    configProps= config(destinationHOST,port,users,passw,upfolder) # upfoder here is not valid . will be changed here
    dynamicUpfolder = CreateArcFolders(configProps, uproot, "Up")  # use tha same function to create upfolders
    configProps = config(destinationHOST, port, users, passw, dynamicUpfolder)
    print ("create upfolders")
# ===== prepare temporary folders from upfolders  =====
    CreateTestFile(upfolders= dynamicUpfolder)
    tempfolder = NewPrepareTempFolders(configProps,temproot)  #make and fill tempfoders() and remove files from upfolders
    arcfolder= CreateArcFolders(configProps,arcroot,arcFileNameHead) # make arcfolder if not exist

    CopyAllFolders(tempfolder, arcfolder) #we do an arc for every user-destination

#    RemoveFromUpfolder(filedict) is in NewPrepareTempFolders
    if (1==1): # do 1 time
        print()
        print()
        print("        *******************************************")
        print("        *        ENVIRO testingSend 1.0           *")
        print("        *   (using multisender tools)             *")
        print("        * generates and sends files automaticaly  *")
        print("        *        DO NOT CLOSE THIS WINDOW         *")
        print("        *******************************************")

        ftp = FTP()

        logging.basicConfig(filename=log, level=logging.INFO, format='%(asctime)s %(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S')


#===========================================================


        for i in range(len(users)):
            try:
                currentSession = session(destinationHOST[i], port[i], users[i], passw[i], tempfolder[i])
                ftpExceptIP = currentSession.user + "-" + currentSession.ip + "-" + currentSession.port

                if ( ftpExceptIP  in ftpExceptIParr) :
                    ## host was not reachable not send it
                    ftpExceptIParr.remove(ftpExceptIP)
                    time.sleep(0.25)
                else:
                    #if host was ok - send
                 #   sendtempfoderFiles()

                    numsent= sendFolderFiles(currentSession)

                    logging.info("," + destinationHOST[i] + "," + users[i] + "," + upfolder[i])
              #      print( "  ", numsent , " files were sent to " ,destinationHOST[i], users[i])
                    print("  ", numsent, " files were sent to ", destinationHOST[i], users[i])


            except ftplib.all_errors as e:
                print(" \n> > > >   F T P exception  - ", destinationHOST[i], users[i],str(e),"\n")

                time.sleep(0.1)

                ftpExceptIParr=  AddToExceptIParr( 10, ftpExceptIP,ftpExceptIParr) #10 ip numbers to array if destination is not reachable

              #  ftpExceptEscapecount = 10
                logging.info("," + destinationHOST[i] + "," + users[i] + "," + upfolder[i] + "," + "Error " + str(e))

        time.sleep(0.15)

        print("-------  SESSION IS FINISHED   ------")






