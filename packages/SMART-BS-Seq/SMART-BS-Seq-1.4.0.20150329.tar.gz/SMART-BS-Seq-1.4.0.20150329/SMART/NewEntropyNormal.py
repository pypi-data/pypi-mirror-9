#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 20131207

@author: liuhongbo
'''
import math


class Entropy():
    '''
    Output the Entropy and the Normal distribution
    '''
    sampleNum=0
    e=0.0001
    MaxMethylationLevel=100

    def __init__(self):
        '''
        Constructor
        '''
        
    def EntropyCalculate(self,dataSet):
        Sum=0; #所有值的和
        H=0;   #该行熵的值
        W=1;   #熵的权重
        X_New=[]  #新的数据数组
        P_New=[]  #新的概率数组
        T_New=[]  #新的概率数组
        Normal_TB_Entropy=self.Tukey_biweight_Normal(dataSet) #计算该行的一步双加权重
        T=Normal_TB_Entropy[-1]  #将最后一个TB赋值给T
#         print "一步双加权重T:"+str(T)

        for i in range(len(dataSet)):
            T_New.append(abs(dataSet[i]));
            if(T_New[i]<self.e):
                T_New[i]=self.e    #将校正后小e的值定义为e，从而降低因为多个0带来的误差
            
        
        
        for i in range(len(dataSet)):         #获取新的数值并计算数组值的和
            X_New.append(abs(dataSet[i]-T));
            if(X_New[i]<1.0):
                X_New[i]=1.0;    #将校正后小0.01的值定义为0.01，从而降低因为多个0带来的误差
            Sum=Sum+X_New[i];
        
#         print "Sum:"+str(Sum)
        
        for i in range(len(dataSet)):
            P_New.append(X_New[i]/Sum);
            #H=H+P_New[i]*(math.log(P_New[i],2));  #累加求熵
            H=H+P_New[i]*(math.log(P_New[i],len(dataSet)));  #累加求熵   
        H=-H;  #和取负成为初始熵
        if H>1.000:
            H=1.000
        MaxReal=max(dataSet);  #获取数组的最大值
        MinReal=min(dataSet);  #获取数组的最小值
        Range=(MaxReal-MinReal)/(self.MaxMethylationLevel-0.0);
        #W=abs(math.log(Range,2))/abs(math.log(0.01,2))
        #W=abs(math.log(Range,2))/abs(math.log(0.01,2));   #计算权重
        #Range=max(H,(MaxReal-MinReal)/(self.MaxMethylationLevel-0.0),0.01)
        W=1-Range;   #计算权重
        T=round(H*W,3);  #借之前TandQ数组，将T值改成H值，相当于返回HandQ
        #print a+"\t"+str(round(H,3))+"\t"+str(round(Range,3))+"\t"+str(round(W,3))+"\t"+str(round(T,3))
        if T>1:
            T=1.000
        Normal_TB_Entropy.append(T)    #将熵值赋给返回数组的最后一个
        return Normal_TB_Entropy;    ####返回的数组:Normal从0到-3，TB为-2，Entropy为-1
        
    def Tukey_biweight_Normal(self,T_New):
        c=5;        #倍数定值
        e=0.0001;  #最小数控制
        MAD=[]
        TandU=[]  #记录T和Q（U）
        W=[]  #每个值的权重数组
        Normal_TB=[]   #用于存储TB和正态分布
        Sum=0;  #所有值的和
        TandU.append(0);
          
        Median=self.getMedian(T_New);    #计算所有数的中位数
        #print Median  
        
        for i in range(len(T_New)):    
            MAD.append(abs(T_New[i]-Median))  #算每个值距离中位数的距离
          
        S=self.getMedian(MAD);     #距离中位数的距离的中位数
        
        
        Fenmu=c*S+e;   #计算每个值的权重
        #print Fenmu
        
        for i in range(1,len(T_New)+1):    
            TandU.append((T_New[i-1]-Median)/Fenmu)
            
            #print TandU[i]
            if(abs(TandU[i])<=1):
                W.append(math.pow((1-math.pow(TandU[i],2)),2));
#                 print W
            else:
                W.append(0);
                Normal_TB.append(0)
            Sum=Sum+W[i-1];
            TandU[0]=TandU[0]+W[i-1]*T_New[i-1];
#             print str(Sum)+"\t"+str(TandU[0])
        #print W
            
        TandU[0]=TandU[0]/Sum;
        Normal_TB=W
        Normal_TB.append(TandU[0])  #The last one is TB
        return Normal_TB
    
    def getMedian(self,dataSet):
        newData=[];
        for i in range(len(dataSet)):    
            newData.append(dataSet[i]);
        newData.sort()  #调用冒泡排序方法对数据进行排序
        if(len(dataSet)%2!=0):
            return newData[len(dataSet)/2];    #奇数个返回中间值
        else:
#             print newData
#             print (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0
            return (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0;  #偶数个返回中间两个的平均值
    
    def EntropyCalculateSet(self,dbSet):
#         print len(dbSet)
        entropy=[]
        for i in range(len(dbSet)):
#             print dbSet[i]
            entropy.append(self.EntropyCalculate(dbSet[i]))
        return entropy
    

if __name__ == '__main__':
    dataSet1=(7.3,69.1,87,69.8,79.8,77.4,70.8,69.6,75.5,79.1,81.2,21,77.6,26.1,2.4,24.5,27.8,16,80.3,54.1,58.9,86.1,37.2,58.8,2.9,53.4,48,81.5,38,60.2,5.6,33.5,3.7,2.2,3.2,6.4,49.5,81.1,76,24.3,85.9,36.3,79.8,73.2,82.2,75.7,79.6,75.3,77.6,75.6)
    dataSet2=(50,50,50,50,50,50,50,50,50,50)
    dataSet3=(90,100,96,95,94,0.36,86,94,89,96)
    dataSet4=(0.5,0.22,0.21,0.22,0.48,98,0.21,0.20,0.58,0.62)
    dataSet5=(0.05,0.022,0.021,0.022,0.048,9.8,0.021,0.02,0.058,0.062)
    dataSet6=(0.0001,0.0001,0.0001,0.0001,0.01,0.0001,0.0001,0.0001,0.0001,0.0001)
    dataSet7=(70.3,60.9,52.9,33.3,0,60.6,43.3)
    dataSetDb=dataSet1,dataSet2,dataSet3,dataSet4,dataSet5,dataSet6,dataSet7
    C1=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C2=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C3=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C4=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C5=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C6=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C7=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C8=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C9=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C10=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C11=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C12=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C13=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C14=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C15=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C16=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C17=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C18=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C19=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C20=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C21=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C22=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C23=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C24=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C25=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C26=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C27=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    #dataSetDb=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20,C21,C22,C23,C24,C25,C26,C27
    DM2=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM3=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM4=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM5=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM6=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM7=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM8=(100,0,0,100,100,0,100,100,100,100,100,100,100,100)
    DM9=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM10=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM11=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM12=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM13=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM14=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM15=(0,100,100,0,0,0,0,0,0,0,0,0,0,0)
    DM16=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM17=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM18=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM19=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM20=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM21=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    DM22=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM23=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM24=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM25=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM26=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM27=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    #dataSetDb1=DM2,DM3,DM4,DM5,DM6,DM7,DM8,DM9,DM10,DM11,DM12,DM13,DM14,DM15,DM16,DM17,DM18,DM19,DM20,DM21,DM22,DM23,DM24,DM25,DM26,DM27
    print "W=abs(math.log(Range,2))/abs(math.log(0.01,2))"
    print "E\tH\tRange\tW\tT"
    entropy=Entropy()
    entropy.MaxMethylationLevel=100
    print entropy.EntropyCalculate(dataSet1)
    #print entropy.EntropyCalculateSet(dataSetDb)

        