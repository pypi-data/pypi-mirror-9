#!/usr/bin/env python
__author__ = 'Matias Carrasco Kind'

from numpy import *
import pyfits as pf

zs,u,g,r,i,z,ug,gr,ri,iz,eu,eg,er,ei,ez,eug,egr,eri,eiz=loadtxt('SDSS_MGS.train',unpack=True)

C=pf.ColDefs([])

CC=pf.Column(name='EU', format='E',array=eu) ; C.add_col(CC)
CC=pf.Column(name='EG', format='E',array=eg) ; C.add_col(CC)
CC=pf.Column(name='ER', format='E',array=er) ; C.add_col(CC)
CC=pf.Column(name='EI', format='E',array=ei) ; C.add_col(CC)
CC=pf.Column(name='EZ', format='E',array=ez) ; C.add_col(CC)
CC=pf.Column(name='EU-G', format='E',array=eug) ; C.add_col(CC)
CC=pf.Column(name='EG-R', format='E',array=egr) ; C.add_col(CC)
CC=pf.Column(name='ER-I', format='E',array=eri) ; C.add_col(CC)
CC=pf.Column(name='G', format='E',array=g) ; C.add_col(CC)
CC=pf.Column(name='R', format='E',array=r) ; C.add_col(CC)
CC=pf.Column(name='I', format='E',array=i) ; C.add_col(CC)
CC=pf.Column(name='Z', format='E',array=z) ; C.add_col(CC)
CC=pf.Column(name='U-G', format='E',array=ug) ; C.add_col(CC)
CC=pf.Column(name='G-R', format='E',array=gr) ; C.add_col(CC)
CC=pf.Column(name='R-I', format='E',array=ri) ; C.add_col(CC)
CC=pf.Column(name='I-Z', format='E',array=iz) ; C.add_col(CC)
CC=pf.Column(name='EI-Z', format='E',array=eiz) ; C.add_col(CC)
CC=pf.Column(name='ZSPEC', format='E',array=zs) ; C.add_col(CC)
CC=pf.Column(name='ZS2', format='E',array=zs) ; C.add_col(CC)
CC=pf.Column(name='ZS3', format='E',array=zs) ; C.add_col(CC)
CC=pf.Column(name='U', format='E',array=u) ; C.add_col(CC)

SS=pf.FITS_rec.from_columns(C)
hdu = pf.BinTableHDU(SS)
hdu.writeto('train.fits',clobber=True)
