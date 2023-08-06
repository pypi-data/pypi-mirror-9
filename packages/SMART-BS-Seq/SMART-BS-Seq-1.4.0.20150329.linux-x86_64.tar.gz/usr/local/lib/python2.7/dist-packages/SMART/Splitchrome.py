#!/usr/bin/env python
'''
Created on 2013.11.12

@author: liuhongbo
'''
import gzip
import os
import sys
import Folderprocess
import time

class Splitchrome():
    def __init__(self):
        '''
        Constructor
        Split the methylation files into different folders named as chrome id
        '''
    def Splitchrome(self,chromes,filenames,OutFolderName):
        '''
        Split the RRBS data
        '''
        #build the dirs with different chrome names
        for i in range(0,len(chromes)):
            dirpath=OutFolderName+chromes[i]
            isExists=os.path.exists(dirpath)
            if not isExists:
                os.mkdir(dirpath)
        
        for filename in filenames:
            print filename
            #build and open the out files
            filedict = {}
            namestart=filename.find('wgEncode')
            for i in range(0,len(chromes)):
                chromemethyfile=OutFolderName+chromes[i]+'/'+chromes[i]+'_'+filename[namestart:]
                chromemethyfile=gzip.open(chromemethyfile,'wb')
                filedict[chromes[i]]=chromemethyfile  #build a dictionary of chrome files: key is chrome, value is the file Handle
            methyfile=gzip.open(filename,'rb') #open current methylation file
            methyfile.readline()
            filecontent=methyfile.readline()
            while filecontent:
                methyinfor=filecontent.split('\t')
                if filedict.has_key(methyinfor[0]) and methyinfor[4]>=10:  #
                    filedict.get(methyinfor[0]).write(methyinfor[1]+"\t"+methyinfor[10])
                filecontent=methyfile.readline()
            for i in range(0,len(chromes)):
                filedict.get(chromes[i]).close
    
    
    def SplitchromeBSSeqWigGz(self,MethyDataFolder,OutFolder,statisticout):
        '''
        Split the BS-SEq data into chromes
        '''
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to split methylation files according to chromes..."
        statisticout.write(Starttime+" Start to split methylation files according to chromes...\n")
        RawMethyDataFolderName=MethyDataFolder+'*.wig.gz'
        OutFolderName=OutFolder+'SplitedMethy/'
        ChromeArray=[]
        SampleNames=[]
        if OutFolderName:
            # use a output directory to store Splited Methylation data 
            if not os.path.exists( OutFolderName ):
                try:
                    os.makedirs( OutFolderName )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % OutFolderName )
        MethyFolder=Folderprocess.Folderprocess()
        RawMethyfilenames=MethyFolder.readFolderfile(RawMethyDataFolderName)
        #build the dirs with different chrome names    
        for filename in RawMethyfilenames:
            # print filename
            #build and open the out files
            namestart=filename.find(MethyDataFolder)+len(MethyDataFolder)
            nameend=filename.find('.wig.gz')
            SampleNames.append(filename[namestart:nameend])
            methyfile=gzip.open(filename,'rb') #open current methylation file
            methyfile.readline()
            filecontent=methyfile.readline()
            CNum=0
            while filecontent:
                if filecontent.find('chr')>=0:  #If search the new chrome,
                    filecontent=filecontent.strip('\n')
                    methychrome=filecontent.split('=')
                    chrome=methychrome[1]
                    Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                    print Starttime+" Spliting "+filename[namestart:]+" "+chrome
                    statisticout.write(Starttime+" Spliting "+filename[namestart:]+" "+chrome+"\n")
                    dirpath=OutFolderName+chrome
                    isExists=os.path.exists(dirpath)
                    if not isExists:
                        os.mkdir(dirpath)
                    ExistchromeTag=0
                    for Existchrome in ChromeArray:
                        if Existchrome==chrome:
                            ExistchromeTag=1
                    if (ExistchromeTag==0):
                        ChromeArray.append(chrome)
                    chromemethyfile=OutFolderName+chrome+'/'+chrome+'_'+filename[namestart:]
                    #print chromemethyfile
                    chromemethyfile=gzip.open(chromemethyfile,'wb')
                else:
                    chromemethyfile.write(filecontent)
                    CNum=CNum+1
                filecontent=methyfile.readline()
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            #print Starttime+" "+filename+"\t"+chrome+"\tC number: "+str(CNum)
            statisticout.write(Starttime+" "+filename[namestart:]+" "+chrome+"\tC number: "+str(CNum)+"\n")
        return ChromeArray,SampleNames

    def run(self,MethyDataFolder,OutFolder,statisticout):
        Splitmethychrome=Splitchrome()
        ChromeArray,SampleNames=Splitmethychrome.SplitchromeBSSeqWigGz(MethyDataFolder,OutFolder,statisticout)
        return ChromeArray,SampleNames

if __name__ == '__main__':
    #chromes=['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']
    #chromes=['chrY']
    Starttime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    print Starttime
    MethyDataFolderName='J:/DNAMethylation/Human/BSSeq/RoadmapBSSeq/20140530_used_90percent/*.wig.gz'
    OutFolderName='J:/DNAMethylation/Human/BSSeq/RoadmapBSSeq/20140530_usedMerged_90percent/'
    MethyFolder=Folderprocess.Folderprocess()
    filenames=MethyFolder.readFolderfile(MethyDataFolderName)
    print "File Num is: "+str(len(filenames))
    #print filenames
    #Splitmethychrome=Splitchrome()
    #Splitmethychrome.Splitchrome(chromes,filenames,OutFolderName)
    statisticout=open(OutFolderName+"statistic.txt",'w')
    a=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    statisticout.write(a)
    statisticout.write(str(len(filenames))+"\n")
    statisticout.write(Starttime+"\n")
    statisticout.close()
    #statisticout.write(filenames+"\n")
    Splitmethychrome=Splitchrome()
    Splitmethychrome.SplitchromeBSSeqWigGz(filenames,OutFolderName)
    Endtime=time.strftime('%Y-%m-%d %A %X',time.localtime(time.time()))
    print "File Num is: "+str(len(filenames))
    print "Start Time is: "+Starttime
    print "End Time is: "+Endtime
    statisticout=open(OutFolderName+"statistic.txt",'a') 
    statisticout.write(str(len(filenames))+"\n")
    statisticout.write(Starttime+"\n")
    statisticout.write(Endtime+"\n")
    statisticout.close()