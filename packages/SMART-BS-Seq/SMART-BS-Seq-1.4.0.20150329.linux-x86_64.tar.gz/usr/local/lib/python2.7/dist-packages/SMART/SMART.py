#!/usr/bin/env python
# Time-stamp: <2014-08-01 13:41:00 Hongbo Liu>

"""Description: SMART main executable

Copyright (c) 2014 Hongbo Liu <hongbo919@gmail.com>

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD License (see the file COPYING included
with the distribution).

@status: release candidate
@version: 1.4.0
@author:  Hongbo Liu
@contact: hongbo919@gmail.com
"""
# ------------------------------------
# python modules
# ------------------------------------
import time
import os
import sys
import argparse
from Splitchrome import Splitchrome
from MethyMergeEntropy import MethyMergeEntropy
from SegmentationNormal import Segmentation
# ------------------------------------
# Main function
# ------------------------------------
def main(argv):
    """The Main function/pipeline for SMART.
    """
    # Parse options...
    description = "%(prog)s -- Specific Methylation Analysis and Report Tool for BS-Sequencing"
    epilog = "For any help, type: %(prog)s -h, or write to Hongbo Liu (hongbo919@gmail.com)"
    parser = argparse.ArgumentParser(description = description, epilog = epilog)
    parser.add_argument("MethyDir",type = str, default = '',
                        help = "The directory (such as /liuhb/BSSeq/) of the folder including methylation data files formated in wig.gz (such as H1.wig.gz). REQUIRED.")
    parser.add_argument("CytosineDir", type = str, default = '',
                        help = "The directory (such as /liuhb/CLoc_hg19/) of the folder including cytosine location files for all chromesomes formated in txt.gz (such as chr1.txt.gz). REQUIRED.")
    parser.add_argument("-n", dest='ProjectName',type = str,
                        help = "Project name, which will be used to generate output file names. DEFAULT: \"SMART\"", default = "SMART" )
    parser.add_argument("-o", dest='OutputFolder',type = str, default = '',
                        help = "If specified all output files will be written to that directory. Default: the directory named using projectname and currenttime (such as SMART20140801132559) in the current working directory")
    parser.add_argument("-v", "--version",dest='version',action='version', version='SMATR 1.4.0')
    UserArgs = parser.parse_args()
    MethyDataFolder=UserArgs.MethyDir
    CFolderName=UserArgs.CytosineDir
    OutFolder=UserArgs.OutputFolder
    ProjectName=UserArgs.ProjectName
    if (MethyDataFolder and CFolderName):
        if MethyDataFolder:
            # use a input directory to input methylation data
            if not os.path.exists( MethyDataFolder ):
                sys.exit( "Methylation data directory (%s) could not be found. Terminating program." % MethyDataFolder )
        if CFolderName:
            # use a input directory to input cytosine data
            if not os.path.exists( CFolderName ):
                sys.exit( "Cytosine directory (%s) could not be found. Terminating program." % CFolderName )
        if (OutFolder==''):
            homedir = os.getcwd()
            Starttime=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            OutFolder=homedir+"/"+ProjectName+Starttime+"/"
            print OutFolder
        if OutFolder:
            # use a output directory to store SMART output
            if not os.path.exists( OutFolder ):
                try:
                    os.makedirs( OutFolder )
                except:
                    sys.exit( "Output directory (%s) could not be created. Terminating program." % OutFolder )            
        
        
        RecordFile=OutFolder+"ProjectReport.txt"
        statisticout=open(RecordFile,'w')
        Starttime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Starttime+" Project "+ProjectName+" Start"
        statisticout.write(Starttime+" Project "+ProjectName+" Start\n")
        
        # Split Methylation data according to chromes...
        Splitchromerun=Splitchrome()
        ChromeArray,SampleNames=Splitchromerun.run(MethyDataFolder, OutFolder, statisticout)
          
        # Merge methylaion data across multiple samples and calculate the methylation specificiy of each common C...
        MethyMergeEntropyrun=MethyMergeEntropy()
        TotalCNum,TotalCommonCNum=MethyMergeEntropyrun.run(ChromeArray,CFolderName,OutFolder,statisticout)
        
        # Genome segmentation based on methylation similarity between neighboring C...
        Segmentationrun=Segmentation()
        SmallSegNum,Numdec,CellTypeHypoNum,CellTypeHyperNum =Segmentationrun.run(ChromeArray,SampleNames,OutFolder,statisticout)
        Endtime=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
        print Endtime+" ********************Project Summary******************"
        print Endtime+" Chromesomes   : "+','.join(ChromeArray)
        print Endtime+" Sample Number : "+str(len(SampleNames))
        print Endtime+" Sample Names  : "+','.join(SampleNames)
        print Endtime+" Number of total Cytosines in all chromesomes: "+str(TotalCNum)
        print Endtime+" Number of Cytosines with methylation in all samples:"+str(TotalCommonCNum)
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
        statisticout.write(Endtime+" Number of total Cytosines in all chromesomes: "+str(TotalCNum)+"\n")
        statisticout.write(Endtime+" Number of Cytosines with methylation in all samples:"+str(TotalCommonCNum)+"\n")
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
        print Endtime+" Project "+ProjectName+" Finished !"
        print Endtime+" Detailed results in "+OutFolder+'FinalResults/'
        print Endtime+" For any questions, contact Hongbo Liu (hongbo919@gmail.com)"
        statisticout.write(Endtime+" Project "+ProjectName+" Finished !\n")
        statisticout.write(Endtime+" The final Results can be found in "+OutFolder+"FinalResults/\n")
        statisticout.write(Endtime+" For any questions, contact Hongbo Liu (hongbo919@gmail.com)\n")
        statisticout.close()

if __name__ == '__main__':
    main(sys.argv)