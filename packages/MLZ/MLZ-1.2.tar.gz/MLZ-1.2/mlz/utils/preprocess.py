"""
.. module:: preprocess
.. moduleauthor:: Matias Carrasco Kind
"""
__author__ = 'Matias Carrasco Kind'

import numpy
import matplotlib.pyplot as plt
import utils_mlz
import data    

class standarize():
    def __init__(self,X):
        self.mean=numpy.mean(X,axis=0)
        self.std=numpy.std(X,axis=0)
        self.X=X
    def transform(self,inputX=None, inputError=None):
        if inputX != None:
            outX = (inputX - self.mean)/self.std
        else:
            outX = ( self.X - self.mean)/self.std
        if inputError == None:
            return outX
        else:
            outEX = inputError/self.std
            return outX,outEX

class scalearray():
    def __init__(self,X, L1 =0 , L2=1):
        self.min = X.min(axis=0)
        self.max = X.max(axis=0)
        self.L1 = L1
        self.L2 = L2
        self.X= X
    def transform(self, inputX=None, inputError= None):
        if inputX != None:
            outX = (inputX - self.min)/(self.max - self.min)
        else:
            outX = (self.X - self.min) / (self.max - self.min)
        if inputError == None:
            return outX*(self.L2 - self.L1) + self.L1
        else:
            outEX=inputError*(self.L2 - self.L1)/(self.max - self.min)
            return outX*(self.L2 - self.L1) + self.L1,outEX
        

class pca_array():
    def __init__(self,X, ndim, tolerance=1.0):
        self.mean = numpy.mean(X,axis=0)
        self.ndim = ndim
        self.tol  = tolerance
        self.Xn = X - self.mean
        self.xC = numpy.cov(self.Xn.T)
        evalues, evectors = numpy.linalg.eig(self.xC)
        idx = numpy.argsort (evalues)
        idx = idx[::-1]
        self.evectors = evectors[:,idx]
        self.evalues = evalues [idx]
        if tolerance < 1.0:
            var_v=numpy.cumsum(self.evalues/sum(self.evalues))
            ww=numpy.where(var_v >= self.tol)[0][0]
            self.ndim = int(ww)+1
        self.evectors = self.evectors [:,:self.ndim]
        
    def transform(self, inputX=None, inputError=None):
        if inputX != None:
            self.Xn = inputX - self.mean
        outX = numpy.dot(self.evectors.T,self.Xn.T)
        #outY = numpy.transpose(numpy.dot(self.evectors,outX))+ self.mean
        if inputError == None:
            return numpy.transpose(outX), self.evalues, self.evectors
        else:
            outEX = numpy.dot(self.evectors.T**2,inputError.T**2)
            return numpy.transpose(outX), numpy.transpose(numpy.sqrt(outEX)),self.evalues, self.evectors


Pars = utils_mlz.read_dt_pars('../test/SDSS_MGS.inputs', verbose=False)
Pars.path_train='../test/'
Pars.path_test='../test/'
Train = data.catalog(Pars, cat_type='train', rank=0)
Test = data.catalog(Pars, cat_type='test', rank=0)
Train.get_XY()
Test.get_XY()

eri=[]

for k in Train.atts: eri.append(Train.AT[k]['eind'])
eri=numpy.array(eri)
Xerr_train=Train.cat_or[:,eri]


eri=[]
for k in Test.atts: eri.append(Test.AT[k]['eind'])
eri=numpy.array(eri)
Xerr_test=Test.cat_or[:,eri]

P=pca_array(Train.X,4)
train_X2,train_EX2,ev1,el1=P.transform(inputX=Train.X, inputError=Xerr_train)
test_X2,test_EX2,ev2,el2=P.transform(inputX=Test.X, inputError=Xerr_test)
train_zs=Train.cat_or[:,Train.AT['zs']['ind']]
test_zs=Test.cat_or[:,Test.AT['zs']['ind']]


