#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2015.3.29

@author: 

'''
import gzip
import scipy.spatial.distance
import NewEntropy
import NewEntropyNormal
import math
from scipy import stats
import numpy as np
import random
import time
import os
import sys


class Segmentation():
    '''
    This module is used merge multiple profiles of the methylation in a chrome into an combined file
    50003153    100
    500170    26
    500190    65
    500191    67
    500198    74
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def _chk_asarray(self, a, axis):
        if axis is None:
            a = np.ravel(a)
            outaxis = 0
        else:
            a = np.asarray(a)
            outaxis = axis
        return a, outaxis
            
    def GenomeSegmentMeanMethy(self,chromes,CellTypeNames,MethySpeInputFolder,MethySegOutputFolder,SegmentBedOutFile,statisticout):
        '''
        For each chromesome, segment it based the methylation entropy, differentroy and EuclideanDistance
        '''
        CellTypeNum=len(CellTypeNames)
        GenomeSegmentOutFolder=MethySegOutputFolder+"GenomeSegment/"
        GenomeSegmentMethyOutFolder=MethySegOutputFolder+"GenomeSegmentMethy/"
        if GenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentOutFolder ):
                try:
                    os.makedirs( GenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentOutFolder )
        if GenomeSegmentMethyOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( GenomeSegmentMethyOutFolder ):
                try:
                    os.makedirs( GenomeSegmentMethyOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % GenomeSegmentMethyOutFolder )
        SmallSegNum=0
        for RegionChrome in chromes:
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Segmenting for "+RegionChrome  #Report the region are segmented
            statisticout.write(Starttime+" Segmenting for "+RegionChrome+"\n")
            EntropyDEEDFile =gzip.open(MethySpeInputFolder+RegionChrome+".txt.gz", 'r')  #Open the corresbondign methylation file
            
            SegmentOUT=open(GenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
            SegmentMethyOUT=gzip.open(GenomeSegmentMethyOutFolder+RegionChrome+".txt.gz", 'w')  #Open the file for segment and methylation
            #Parameter initialization
            EntropySum=0
            MethySumList=[0]*CellTypeNum
            MethyList=[0]*CellTypeNum
            SegmentCpGlist=[]
            Methyentropy=NewEntropy.Entropy()
            #Perform segmentation
            CurrentCline=EntropyDEEDFile.readline()     #Read the first line (Colomn Name) of the methylation file
            PreviousState=''
            PreviousLocation=0
            CurrentCline=EntropyDEEDFile.readline()     #Read the first data line
            while CurrentCline:
                CurrentCline=CurrentCline.strip('\n')      #
                MethyEntropyInfor=CurrentCline.split()
                CurrentLocation=int(MethyEntropyInfor[0])
                MethyList=[ float(x) for x in MethyEntropyInfor[6:-3]]
                
                Entropy=float(MethyEntropyInfor[-3])
                DifferEntropy=float(MethyEntropyInfor[-2])
                EuclidDistance=float(MethyEntropyInfor[-1])
                #Determine the cell-specificity of current CpG
                if Entropy>0.75:
                    CurrentState='HigSpe'
                elif Entropy>=0.5:
                    CurrentState='LowSpe'
                else:
                    CurrentState='NotSpe'
                    
                #Merge the neighboring CpG with the same cell-specificity
                if CurrentState==PreviousState and (DifferEntropy>0.4 and EuclidDistance<0.2) and (CurrentLocation-PreviousLocation)<=500:  #If the states are the same and the methylation are similar, merge them
                    EntropySum=EntropySum+Entropy      #Sum the entropy
                    MethySumList=[x+y for x, y in zip(MethySumList, MethyList)]  #Sum the methylaion in each cell type
                    SegmentCpGlist.append(MethyEntropyInfor[0])  #Record current CpG and merge it
                    #print SegmentCpGlist
                else:     #If the merger condition is not filled, output current segment, and initialize the new segment
                    #output current segment
                    SegmentCpGNum=len(SegmentCpGlist)
                    #print SegmentCpGlist
                    if len(SegmentCpGlist)>0:
                        MethySumList=[round(float(x)/SegmentCpGNum,3) for x in MethySumList ]
                        MethySumListforEntropy=[x*100.0 for x in MethySumList ]
                        MethySumListforEntropy=tuple(MethySumListforEntropy)
                        MethySpecificity=round(1.0-Methyentropy.EntropyCalculate(MethySumListforEntropy),3)       #Caculate the new MethySpecificity for mean methylation                 
                        SegmentInfor=RegionChrome+":"+SegmentCpGlist[0]+"-"+SegmentCpGlist[-1]+"\t"+str(MethySpecificity)+"\t"+str(SegmentCpGNum)
                        SmallSegNum=SmallSegNum+1
                        print >>SegmentOUT, SegmentInfor
                        print >>SegmentMethyOUT, SegmentInfor,MethySumList
                        if (float(MethySpecificity)>0.75):
                            RegionColor='0,0,255'
                            SegmentState='HighSpe'
                        elif (float(MethySpecificity)>=0.5):
                            RegionColor='173,216,230'
                            SegmentState='LowSpe'
                        else:
                            RegionColor='255,165,0'
                            SegmentState='NoSpe'
                        RegionName=SegmentState+':'+str(SegmentCpGNum)
                        SegmentBedOutFile.write(RegionChrome+"\t"+SegmentCpGlist[0]+"\t"+SegmentCpGlist[-1]+"\t"+RegionName+"\t"+str(MethySpecificity)+"\t"+'+'+"\t"+SegmentCpGlist[0]+"\t"+SegmentCpGlist[-1]+"\t"+RegionColor+"\n")
                    #initialize the new segment
                    EntropySum=0
                    MethySumList=[0]*CellTypeNum
                    SegmentCpGlist=[]
                    EntropySum=EntropySum+Entropy      #Sum the entropy
                    MethySumList=[x+y for x, y in zip(MethySumList, MethyList)]  #Sum the methylaion in each cell type
                    SegmentCpGlist.append(MethyEntropyInfor[0])  #Record current CpG and merge it                                                                                                       
                PreviousState=CurrentState
                PreviousLocation=CurrentLocation
                CurrentCline=EntropyDEEDFile.readline()
        return SmallSegNum

                
    def SegmentMerge(self,chromes,CellTypeNames,MethySegOutputFolder,statisticout):
        '''
        For each chromesome, Merge the segments based on the methylation entropy, differentroy and EuclideanDistance
        '''
        CellTypeNum=len(CellTypeNames)
        MergedGenomeSegmentOutFolder=MethySegOutputFolder+"MergedGenomeSegment/"
        if MergedGenomeSegmentOutFolder:
            # use a output directory to store merged Methylation data 
            if not os.path.exists( MergedGenomeSegmentOutFolder ):
                try:
                    os.makedirs( MergedGenomeSegmentOutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % MergedGenomeSegmentOutFolder )
        Methyentropy=NewEntropy.Entropy()
        for RegionChrome in chromes:
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Merging Segments for "+RegionChrome  #Report the region are segmented
            statisticout.write(Starttime+" Merging Segments for "+RegionChrome+"\n")
            file=gzip.open(MethySegOutputFolder+"GenomeSegmentMethy/"+RegionChrome+".txt.gz", 'r')  #Open the file for segment and methylation
            MergedSegmentOUT =open(MergedGenomeSegmentOutFolder+RegionChrome+".txt", 'w')  #Open the file for the segment
            list0=[]
            length=len(list0)
            n=0
            line=file.readline()
            while n<=(7-length) and line:
                line=line.strip('\n')
                line0=line.split('\t')
                a1=line0[0].split(':')
                a2=a1[-1].split('-')
                a1=a1+a2
                del a1[1]
                line1=line0[-1].split(' [')
                a=line1[-1].strip(']')
                a=a.split(', ')
                a1.append(line0[1])
                a1.append(line1[0])
                a1=a1+a
                list0.append(a1)
                n=n+1
                line=file.readline()
            j=1
            CpGNum=0
            while j<=(len(list0)-1):
                PreviousMethydataSet=list0[0][5:len(list0[0])]
                for i in range(len(PreviousMethydataSet)):
                    PreviousMethydataSet[i]=float(PreviousMethydataSet[i])*100.0
                    PreviousMethydataSet[i]=round(PreviousMethydataSet[i],3)
                entropy=float(list0[0][3])
                if entropy<0.25:
                    PreviousState='HigSpe'
                elif entropy<=0.5:
                    PreviousState='LowSpe'
                else:
                    PreviousState='NotSpe'
                    
                MethydataSet=list0[j][5:len(list0[0])]
                
                for i in range(len(MethydataSet)):
                    MethydataSet[i]=float(MethydataSet[i])*100.0
                    MethydataSet[i]=round(MethydataSet[i],3)
                entropy=float(list0[j][3])
                if entropy<0.25:
                    CurrentState='HigSpe'
                elif entropy<=0.5:
                    CurrentState='LowSpe'
                else:
                    CurrentState='NotSpe'    
                SqrtSampleTotalNum=math.sqrt(CellTypeNum)
                EucDistance=scipy.spatial.distance.euclidean(PreviousMethydataSet, MethydataSet)/100/SqrtSampleTotalNum
                DifferMethydataSet=list(map(lambda x: abs(x[0]-x[1]), zip(PreviousMethydataSet, MethydataSet)))
                DifferMethydataSet=tuple(DifferMethydataSet)
                DifferEntropyvalue=Methyentropy.EntropyCalculate(DifferMethydataSet)
                
                if CurrentState==PreviousState and DifferEntropyvalue>0.4 and EucDistance<0.2 and (int(list0[j][1])-int(list0[0][2]))<=500:
                    avEntropyvalue=(float(list0[0][3])*float(list0[0][4])+float(list0[j][3])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                    avEntropyvalue=round(avEntropyvalue,3)
                    count=int(list0[0][4])+int(list0[j][4])
                    a1=[list0[0][0],list0[0][1],list0[j][2],avEntropyvalue,count]
                    b1=list0[0][5:len(list0[0])]
                    b2=list0[j][5:len(list0[0])]
                    for q in range(len(b1)):
                        b1[q]=(float(b1[q])*float(list0[0][4])+float(b2[q])*float(list0[j][4]))/(float(list0[0][4])+float(list0[j][4]))
                        b1[q]=round(b1[q],3)
                    newlist=a1+b1
                    list0[j]=newlist
                    list0=list0[j:len(list0)]
                    length=len(list0)
                    n=0
                    line=file.readline()
                    while n<=(7-length) and line:                        
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                elif j==(len(list0)-1):
                    MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                    Methydata='\t'.join(MethyList)
                    Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                    MeanSpecificity=str(list0[0][3])
                    CpGNum=str(list0[0][4])
                    MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")
                    list0=list0[1:len(list0)]
                    n=0
                    line=file.readline()
                    while n<=(7-len(list0))and line:
                        line=line.strip('\n')
                        line0=line.split('\t')
                        a1=line0[0].split(':')
                        a2=a1[-1].split('-')
                        a1=a1+a2 
                        del a1[1]
                        line1=line0[-1].split(' [')
                        a=line1[-1].strip(']')
                        a=a.split(', ')
                        a1.append(line0[1])
                        a1.append(line1[0])
                        a1=a1+a
                        list0.append(a1)
                        n=n+1
                        line=file.readline()
                    j=1
                else:
                    j=j+1
            if len(list0)==1:
                MethyList=[str(x) for x in list0[0][5:len(list0[0])]]
                Methydata='\t'.join(MethyList)
                Segmentname=list0[0][0]+":"+list0[0][1]+"-"+list0[0][2]
                MeanSpecificity=str(list0[0][3])
                CpGNum=str(list0[0][4])
                MergedSegmentOUT.write(Segmentname+"\t"+MeanSpecificity+"\t"+CpGNum+"\t"+Methydata+"\n")

                
    def FoldertxttoBed9withMethyandSpecificity(self, InputFolder,BedOutFile,MergedSegmentOutFile,MergedSegmentwithmethylationOutFile,MergedHighLowSpeSegmentwithspecificityOutFile,SegmentCellTypeMethymarkPvalue,chromes,CellTypeNames,statisticout):
        '''
        
        '''
        Methyentropy=NewEntropyNormal.Entropy()
        Numdec={'MergedSegment':0, 'HighSpe':0, 'LowSpe':0, 'NoSpe':0, 'UniHypo':0, 'UnipLow':0,'UnipHigh':0,'UniHyper':0, 'MethyMark':0, 'HypoMark':0, 'HyperMark':0}
        CellTypeHypoNum={}
        CellTypeHyperNum={}
        for CellTypeName in CellTypeNames:
            CellTypeHypoNum[CellTypeName]=0
            CellTypeHyperNum[CellTypeName]=0
        
        for chrome in chromes:
            Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            print Starttime+" Generating Results for "+chrome
            statisticout.write(Starttime+" Generating Results for "+chrome+"\n")
            InputFilename=InputFolder+chrome+".txt"
            InputFile=open(InputFilename,'r')
            RegionFileLine=InputFile.readline()
            while RegionFileLine:
                #chrM:33-14946 0.0 684 [0.009, 0.006, 0.009, 0.011,
                Numdec['MergedSegment']=Numdec['MergedSegment']+1
                RegionFileLine=RegionFileLine.strip('\n')
                RegionFileLine=RegionFileLine.replace(":",'\t')
                RegionFileLine=RegionFileLine.replace('-','\t')
                RegionFileLine=RegionFileLine.replace(']','')
                RegionFileLine=RegionFileLine.replace("\'",'')
                RegionFileLine=RegionFileLine.replace('[','')
                RegionFileLine=RegionFileLine.replace(', ','\t')
                #print RegionFileLine
                CurrentRegionrawinfor=RegionFileLine.split('\t')
                RegionChrome=CurrentRegionrawinfor[0]
                RegionStart=CurrentRegionrawinfor[1]
                RegionEnd=CurrentRegionrawinfor[2]
                RegionCNum=CurrentRegionrawinfor[4]
                MethylationRawList=CurrentRegionrawinfor[5:len(CurrentRegionrawinfor)]
                Methydata=','.join(MethylationRawList)
                MethyList=[]
                for CelltNum in range(0,len(MethylationRawList)):
                    MethylationRawList[CelltNum]=float(MethylationRawList[CelltNum])
                    MethyList.append(MethylationRawList[CelltNum]*100)
                MethydataSet=tuple(MethyList)
                Normal_TB_Entropy=Methyentropy.EntropyCalculate(MethydataSet)
                MethySpecificity=round(1.0-Normal_TB_Entropy[-1],3)       #Caculate the new MethySpecificity for mean methylation      
                Tukey_biweight= float(Normal_TB_Entropy[-2])/100
                RegionStrand='+'
                MeanMethy=round(sum(MethylationRawList)/len(MethylationRawList),3)
                if (float(MethySpecificity)>0.75):
                    RegionColor='0,0,255'
                    SpecificityState='HighSpe'
                    MethyState='HighSpe'
                    Numdec['HighSpe']=Numdec['HighSpe']+1
                elif (float(MethySpecificity)>=0.5):
                    RegionColor='0,255,255'
                    SpecificityState='LowSpe'
                    MethyState='LowSpe'
                    Numdec['LowSpe']=Numdec['LowSpe']+1
                else:
                    SpecificityState='NoSpe'
                    Numdec['NoSpe']=Numdec['NoSpe']+1
                    if MeanMethy<=0.25:
                        RegionColor='0,255,0'
                        MethyState='UniHypo'
                        Numdec['UniHypo']=Numdec['UniHypo']+1
                    elif MeanMethy>0.25 and MeanMethy<=0.6:
                        RegionColor='34,139,34'
                        MethyState='UnipLow'
                        Numdec['UnipLow']=Numdec['UnipLow']+1
                    elif MeanMethy>0.6 and MeanMethy<=0.8:
                        RegionColor='255,165,0'
                        MethyState='UnipHigh'
                        Numdec['UnipHigh']=Numdec['UnipHigh']+1
                    else:
                        RegionColor='255,0,0'
                        MethyState='UniHyper'
                        Numdec['UniHyper']=Numdec['UniHyper']+1
                SegmentLength=int(RegionEnd)-int(RegionStart)+1
                ###Calculate the CellTypeSpecificityPvalue
                Normalbase=Normal_TB_Entropy[0:-2]
                NormalList=[]
                for CelltNum in range(0,len(MethylationRawList)):
                    if Normalbase[CelltNum]>=0.5:
                        RandomLevel=random.randint(0,5)
                        if (RandomLevel==0):
                            NormalList.append(MethylationRawList[CelltNum])
                        elif(RandomLevel==1):
                            NormalList.append(MethylationRawList[CelltNum]+0.001)
                        elif(RandomLevel==2):
                            NormalList.append(MethylationRawList[CelltNum]-0.005)
                        elif(RandomLevel==3):
                            NormalList.append(MethylationRawList[CelltNum]-0.001)
                        elif(RandomLevel==4):
                            NormalList.append(MethylationRawList[CelltNum]+0.005)
                        else:
                            NormalList.append(MethylationRawList[CelltNum]-0.001)
                #print NormalList
                CellTypeSpecificityPvalueList=[]                    
                for CelltNum in range(0,len(MethylationRawList)):
                    CellTypeName=CellTypeNames[CelltNum]
                    Methylation=MethylationRawList[CelltNum]
                    if Normalbase[CelltNum]>=0.5:
                        CellTypeSpecificityPvalueList.append('1')
                    else:
                        a=NormalList
                        axis=0
                        a, axis = Segmentation()._chk_asarray(a, axis)
                        n=a.shape[axis]
                        v = np.var(a, axis, ddof=1)
                        denom = np.sqrt(v / float(n))
                        if denom==0:
                            pvalue=1
                        else:
                            one_sample_Ttest=stats.ttest_1samp(NormalList,float(Methylation))
                            pvalue=one_sample_Ttest[1]
                        if (pvalue==0):
                            pvalue=1.0e-100
                        if ((Tukey_biweight-Methylation)>=0.3):
                            CellTypeSpecificityPvalueList.append('-'+"{:.2e}".format(pvalue))
                            Pvalueformated="{:.2e}".format(pvalue)
                            MethyMarkType="HypoMark"
                        elif ((Methylation-Tukey_biweight)>=0.3):
                            CellTypeSpecificityPvalueList.append("{:.2e}".format(pvalue))
                            Pvalueformated="{:.2e}".format(pvalue)
                            MethyMarkType="HyperMark"
                        #Only output the segment with more than 5 CpGs and 20bp
                        if (float(MethySpecificity)>=0.5 and int(RegionCNum)>=10 and int(SegmentLength)>=20 and pvalue<=1.0e-3 and abs(Methylation-Tukey_biweight)>=0.3):
                        #if (float(MethySpecificity)>=0.5 and int(RegionCNum)>=10 and int(SegmentLength)>=20):
                            SegmentCellTypeMethymarkPvalue.write(RegionChrome+"\t"+RegionStart+"\t"+RegionEnd+"\t"+SpecificityState+"\t"+CellTypeName+"\t"+MethyMarkType+"\t"+Pvalueformated+"\n")
                            Numdec['MethyMark']=Numdec['MethyMark']+1
                            if MethyMarkType=="HypoMark":
                                Numdec['HypoMark']=Numdec['HypoMark']+1
                                CellTypeHypoNum[CellTypeName]=CellTypeHypoNum[CellTypeName]+1
                            elif MethyMarkType=="HyperMark":
                                Numdec['HyperMark']=Numdec['HyperMark']+1
                                CellTypeHyperNum[CellTypeName]=CellTypeHyperNum[CellTypeName]+1
                            
                ##############OUTPUT
                if (int(RegionCNum)>=10 and int(SegmentLength)>=20):   #Only output the segment with more than 5 CpGs and 20bp
                    RegionName=MethyState+':S='+str(round(MethySpecificity,1))+',M='+str(round(MeanMethy,1))+',L='+str(SegmentLength)
                    ##########Output the segments with core infor
                    BedOutFile.write(RegionChrome+"\t"+RegionStart+"\t"+RegionEnd+"\t"+RegionName+"\t"+str(int(MeanMethy*1000))+"\t"+RegionStrand+"\t"+RegionStart+"\t"+RegionEnd+"\t"+RegionColor+"\n")
                    MergedSegmentOutFile.write(RegionChrome+"\t"+RegionStart+"\t"+RegionEnd+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(MeanMethy)+"\t"+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+RegionColor+"\n")
                    ##########Output the segments with core infor and methylation data
                    MergedSegmentwithmethylationOutFile.write(RegionChrome+"\t"+RegionStart+"\t"+RegionEnd+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(MeanMethy)+"\t"+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+Methydata+"\n")
                    ##########Output the segments with core infor and cell-type-specificity
                    if (float(MethySpecificity)>=0.5):
                        CellTypeSpecificityPvalue=','.join(CellTypeSpecificityPvalueList)
                        MergedHighLowSpeSegmentwithspecificityOutFile.write(RegionChrome+"\t"+RegionStart+"\t"+RegionEnd+"\t"+SpecificityState+"\t"+MethyState+"\t"+str(MethySpecificity)+"\t"+str(MeanMethy)+"\t"+str(RegionCNum)+"\t"+str(SegmentLength)+"\t"+CellTypeSpecificityPvalue+"\n")
                RegionFileLine=InputFile.readline()
        return Numdec,CellTypeHypoNum,CellTypeHyperNum
        

    def median(self,sequence):
            if len(sequence) < 1:
                return None
            else:
                sequence.sort()
                return sequence[len(sequence) // 2]
    
    
    def run(self,chromes,CellTypeNames,OutFolder,statisticout):
        MethySpeInputFolder=OutFolder+'MethylationSpecificity/'
        MethySegOutputFolder=OutFolder+'MethylationSegment/'
        FinalResultFolder=OutFolder+'FinalResults/'
        if MethySegOutputFolder:
                # use a output directory to store merged Methylation data 
                if not os.path.exists( MethySegOutputFolder ):
                    try:
                        os.makedirs( MethySegOutputFolder )
                    except:
                        sys.exit( "Output directory (%s) could not be created. Terminating program." % MethySegOutputFolder )
        if FinalResultFolder:
                # use a output directory to store merged Methylation data 
                if not os.path.exists( FinalResultFolder ):
                    try:
                        os.makedirs( FinalResultFolder )
                    except:
                        sys.exit( "Output directory (%s) could not be created. Terminating program." % FinalResultFolder )
        # Genome segmentation based on methylation similarity between neighboring C...
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start genome segmentation ..."
        statisticout.write(Starttime+" Start genome segmentation ...\n")
        SegmentBedOutFile=gzip.open(FinalResultFolder+"1SmallSegmentBed.txt.gz",'wb') #Biult a bed file    
        SegmentBedOutFile.write("track name=\"MethySegment\" description=\"Methylation Segment of Across Samples\" visibility=2 itemRgb=\"On\"\n")
        Searchregion=Segmentation()
        SmallSegNum=Searchregion.GenomeSegmentMeanMethy(chromes,CellTypeNames,MethySpeInputFolder,MethySegOutputFolder,SegmentBedOutFile,statisticout)
        SegmentBedOutFile.close()
        
        #Merging Segmentation
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to merge small segments into larger ones..."
        statisticout.write(Starttime+" Start to merge small segments into larger ones...\n")
        Searchregion.SegmentMerge(chromes,CellTypeNames,MethySegOutputFolder,statisticout)
        
        #Generate the final result
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Start to generate the final results..."
        statisticout.write(Starttime+" Start to generate the final results...\n")
        InputFolder=MethySegOutputFolder+"MergedGenomeSegment/"
        BedOutFile=gzip.open(FinalResultFolder+"2MergedSegmentBed.txt.gz",'wb') #Biult a bed file
        BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Across Samples\" visibility=2 itemRgb=\"On\"\n")
        #BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Human Cells/Tissues (0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")
        ######Bed9 for Visualization in Hub of UCSC genome browser
        MergedSegmentOutFile=open(FinalResultFolder+"3MergedSegment.txt",'w') #Biult a bed file    
        MergedSegmentOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tMedianMethy\tCNum\tLength\tRegionColor\n")    
        ######SegmentwithMethylation data
        MergedSegmentwithmethylationOutFile=open(FinalResultFolder+"4MergedSegmentwithmethylation.txt",'w') #Biult a bed file    
        MergedSegmentwithmethylationOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tCNum\tLength\t"+','.join(CellTypeNames)+"\n")    
        ######Cell-type-specificity
        MergedHighLowSpeSegmentwithspecificityOutFile=open(FinalResultFolder+"5MergedHighLowSpeSegmentwithspecificity.txt",'w') #Biult a bed file    
        MergedHighLowSpeSegmentwithspecificityOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tCNum\tLength\tPvalue:"+','.join(CellTypeNames)+"\n")    
        ######Cell-type-specificity2
        SegmentCellTypeMethymarkPvalue=open(FinalResultFolder+"6CellTypeSpecificMethymarkPvalue.txt",'w') #Biult a bed file    
        SegmentCellTypeMethymarkPvalue.write("RegionChrome\tRegionStart\tRegionEnd\tSpecificityState\tCellTypeName\tMethyMarkType\tPvalue\n")    
        Numdec,CellTypeHypoNum,CellTypeHyperNum=Searchregion.FoldertxttoBed9withMethyandSpecificity(InputFolder,BedOutFile,MergedSegmentOutFile,MergedSegmentwithmethylationOutFile,MergedHighLowSpeSegmentwithspecificityOutFile,SegmentCellTypeMethymarkPvalue,chromes,CellTypeNames,statisticout)
        BedOutFile.close()
        return SmallSegNum,Numdec,CellTypeHypoNum,CellTypeHyperNum


if __name__ == '__main__':
    ChromeArray=['chrM','chrY']
    SampleNames=['CellType1','CellType2','CellType3','CellType4','CellType5','CellType6','CellType7','CellType8','CellType9','CellType10','CellType11','CellType12','CellType13','CellType14','CellType15','CellType16','CellType17','CellType18','CellType19']
    OutFolder="J:\\MouseMethymarkData\\MouseMethyMark\\"
    RecordFile=OutFolder+"ProjectReport.txt"
    statisticout=open(RecordFile,'w')
    SmallSegNum=0
    Numdec=0
    CellTypeHypoNum=0
    CellTypeHyperNum=0
    
    Segmentationrun=Segmentation()
    SmallSegNum,Numdec,CellTypeHypoNum,CellTypeHyperNum =Segmentationrun.run(ChromeArray,SampleNames,OutFolder,statisticout)
    Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
    print Endtime+" ********************Project Summary******************"
    print Endtime+" Chromesomes   : "+','.join(ChromeArray)
    print Endtime+" Sample Number : "+str(len(SampleNames))
    print Endtime+" Sample Names  : "+','.join(SampleNames)
    #print Endtime+" Number of total Cytosines in all chromesomes: "+str(TotalCNum)
    #print Endtime+" Number of Cytosines with methylation in all samples:"+str(TotalCommonCNum)
    print Endtime+" Small  Segment Number             : "+str(SmallSegNum)
    print Endtime+" Merged Segment Number             : "+str(Numdec['MergedSegment'])
    print Endtime+" HighSpe Segment Number            : "+str(Numdec['HighSpe'])
    print Endtime+" LowSpe  Segment Number            : "+str(Numdec['LowSpe'])
    print Endtime+" NoSpe   Segment Number            : "+str(Numdec['NoSpe'])
    print Endtime+" NoSpe-UniHypo  Segment Number     : "+str(Numdec['UniHypo'])
    print Endtime+" NoSpe-UnipLow  Segment Number     : "+str(Numdec['UnipLow'])
    print Endtime+" NoSpe-UnipHigh Segment Number     : "+str(Numdec['UnipHigh'])
    print Endtime+" NoSpe-UniHyper Segment Number     : "+str(Numdec['UniHyper'])
    print Endtime+" MethyMark Segment Number          : "+str(Numdec['MethyMark'])
    print Endtime+" MethyMark-HypoMark  Segment Number: "+str(Numdec['HypoMark'])
    print Endtime+" MethyMark-HyperMark Segment Number: "+str(Numdec['HyperMark'])
    statisticout.write(Endtime+" ********************Project Summary******************\n")
    statisticout.write(Endtime+" Chromesomes:  "+','.join(ChromeArray)+"\n")
    statisticout.write(Endtime+" SampleNumber: "+str(len(SampleNames))+"\n")
    statisticout.write(Endtime+" SampleNames:  "+','.join(SampleNames)+"\n")
    #statisticout.write(Endtime+" Number of total Cytosines in all chromesomes: "+str(TotalCNum)+"\n")
    #statisticout.write(Endtime+" Number of Cytosines with methylation in all samples:"+str(TotalCommonCNum)+"\n")
    statisticout.write(Endtime+" Small Segment Number              : "+str(SmallSegNum)+"\n")
    statisticout.write(Endtime+" Merged Segment Number             : "+str(Numdec['MergedSegment'])+"\n")
    statisticout.write(Endtime+" HighSpe Segment Number            : "+str(Numdec['HighSpe'])+"\n")
    statisticout.write(Endtime+" LowSpe Segment Number             : "+str(Numdec['LowSpe'])+"\n")
    statisticout.write(Endtime+" NoSpe Segment Number              : "+str(Numdec['NoSpe'])+"\n")
    statisticout.write(Endtime+" NoSpe-UniHypo Segment Number      : "+str(Numdec['UniHypo'])+"\n")
    statisticout.write(Endtime+" NoSpe-UnipLow Segment Number      : "+str(Numdec['UnipLow'])+"\n")
    statisticout.write(Endtime+" NoSpe-UnipHigh Segment Number     : "+str(Numdec['UnipHigh'])+"\n")
    statisticout.write(Endtime+" NoSpe-UniHyper Segment Number     : "+str(Numdec['UniHyper'])+"\n")
    statisticout.write(Endtime+" MethyMark Segment Number          : "+str(Numdec['MethyMark'])+"\n")
    statisticout.write(Endtime+" MethyMark-HypoMark Segment Number : "+str(Numdec['HypoMark'])+"\n")
    statisticout.write(Endtime+" MethyMark-HyperMark Segment Number: "+str(Numdec['HyperMark'])+"\n")
    for i in CellTypeHypoNum: 
        print Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])
        statisticout.write(Endtime+" "+i+" HypoMark  Number: "+str(CellTypeHypoNum[i])+"\n")
        print Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])
        statisticout.write(Endtime+" "+i+" HyperMark Number: "+str(CellTypeHyperNum[i])+"\n")
    print Endtime+" *********************Summary End*********************"
    statisticout.write(Endtime+" *********************Summary End*********************\n")
    #print Endtime+" Project "+ProjectName+" Finished !"
    print Endtime+" Detailed results in "+OutFolder+'FinalResults/'
    print Endtime+" For any questions, contact Hongbo Liu (hongbo919@gmail.com)"
    #statisticout.write(Endtime+" Project "+ProjectName+" Finished !\n")
    statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"FinalResults/\n")
    statisticout.write(Endtime+" For any questions, contact Hongbo Liu (hongbo919@gmail.com)\n")
    statisticout.close()

    '''
    #print "Genome Segmentation"
    CellTypeNames=['Left.Ventricle.1','Thymus','Ovary','Adrenal.Gland','Adipose.Tissue','Gastric','Psoas.Muscle','Right.Atrium','Right.Ventricle','Sigmoid.Colon.1','hESC_CD56..Ectoderm.1','Hippocampus.Middle.1','hESC_CD56..Mesoderm.1','HUES64','hESC_CD56..Mesoderm.2','hESC_CD184..Endoderm.1','hESC_CD56..Ectoderm.2','Breast.Myoepithelial','Neurosphere.GanEmi.1','Keratinocyte.Cells','Spermatozoa.Cells','Neurosphere.Cortex.1','Neurosphere.GanEmi.2','UCSF.4..ESC','Neurosphere.Cortex.2','Luminal.Epithelial','Fetal.Thymus','Fetal.Muscle.Leg','H1','IMR90','H1.BMP4','H1.Derived.NPCs','iPS.DF.19.11','iPS.DF.6.9','H9','H1.BMP4.Mesendoderm','H1.Mesenchymal.SCs','Adult.Liver','Hippocampus.Middle.2','hESC_CD184..Endoderm.2','CD34.Primary.Cells','Brain_Germinal.Matrix','Sigmoid.Colon.2','Small.Intestine','Lung','Aorta','Esophagus','Left.Ventricle.2','Pancreas','Spleen']
    chromes=['chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY']
    #chromes=['chrY','chrM']
    #chromes=['chr6']
    #SegmentBedOutFile=gzip.open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\GenomeSegment20140406\\SegmentBed_0.4&0.2.txt.gz",'wb') #Biult a bed file    
    #SegmentBedOutFile.write("track name=\"MethySegment_0.4&0.2&500\" description=\"Methylation Segment of Human Cells/Tissues (_0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")

    Searchregion=Segmentation()
    #Searchregion.GenomeSegmentMeanMethy(chromes,SegmentBedOutFile)
    #SegmentBedOutFile.close()
    print "Merging Segmentation"
    #Searchregion.SegmentMerge(chromes)
    
    print "Biuding BED formated Segmentation"
    InputFolder="D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\"
    BedOutFile=gzip.open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\MergedSegmentBed.txt.gz",'wb') #Biult a bed file    
    #BedOutFile.write("track name=\"MergedMethySegment\" description=\"Merged Methylation Segment of Human Cells/Tissues (0.4&0.2&500)\" visibility=2 itemRgb=\"On\"\n")
    ######Bed9 for Visualization in Hub of UCSC genome browser
    MergedSegmentOutFile=open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\MergedSegment.txt",'w') #Biult a bed file    
    MergedSegmentOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tMedianMethy\tCNum\tLength\tRegionColor\n")    
    ######SegmentwithMethylation data
    MergedSegmentwithmethylationOutFile=open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\MergedSegmentwithmethylation.txt",'w') #Biult a bed file    
    MergedSegmentwithmethylationOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tCNum\tLength\tMethydata\n")    
    ######Cell-type-specificity
    MergedHighLowSpeSegmentwithspecificityOutFile=open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\MergedHighLowSpeSegmentwithspecificity.txt",'w') #Biult a bed file    
    MergedHighLowSpeSegmentwithspecificityOutFile.write("Chrome\tStart\tEnd\tSpecificityState\tMethyState\tMethySpecificity\tMeanMethy\tCNum\tLength\tCellTypeSpecificityPvalue\n")    
    ######Cell-type-specificity2
    SegmentCellTypeMethymarkPvalue=open("D:\\GenomeSegment_DEED\\20140406_0.4&0.2&500\\MergedGenomeSegmentMethy20140406\\SegmentCellTypeMethymarkPvalue.txt",'w') #Biult a bed file    
    SegmentCellTypeMethymarkPvalue.write("RegionChrome\tRegionStart\tRegionEnd\tSpecificityState\tCellTypeName\tMethyMarkType\tPvalue\n")    
    
    #Searchregion.FoldertxttoBed9(InputFolder,BedOutFile,MergedSegmentOutFile,chromes)
    Searchregion.FoldertxttoBed9withMethyandSpecificity(InputFolder,BedOutFile,MergedSegmentOutFile,MergedSegmentwithmethylationOutFile,MergedHighLowSpeSegmentwithspecificityOutFile,SegmentCellTypeMethymarkPvalue,chromes,CellTypeNames)
    BedOutFile.close()
    '''