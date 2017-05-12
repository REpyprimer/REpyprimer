__doc__ = r"""
.. _dumper
:mod:`dumper` -- REpyprimer dump module
============================================ 

... module:: rcombine
    :platform: Unix, Windows
    :synopsis: Provide combine like functionality for REpyprimer
... moduleauthor:: Jaegun Jung <jjung@ramboll.com>

"""

__all__=['rcombine',]
from pandasql import sqldf
from PseudoNetCDF.camxfiles.Memmaps import *
from _exprparse import *

import sys
if sys.version_info.major == 3:
    from io import BytesIO as StringIO
    commaspace = u', '
    semicolon = b';'
else:
    from StringIO import StringIO
    commaspace = ', '
    semicolon = ';'
    BrokenPipeError = None
import numpy as np
import pandas as pd
import netCDF4 as ncdf4
import csv
import re
import os
import datetime

# Remove values from list
def remove_values_from_list(the_list, val):
    while val in the_list:
       the_list.remove(val)

def blank_file(fin_path, input_format, fout_path, novars, lsurf):
        #create blank file
        if input_format == "netcdf": fin = ncdf4.Dataset(fin_path)              
        else: fin  = uamiv(fin_path)                                            
        fout = ncdf4.Dataset(fout_path,'w',format="NETCDF3_CLASSIC")

        #copy dimensions
        dimensions_keys = "TSTEP DATE-TIME LAY VAR ROW COL".split() # These dimension keys must be in the file to be used by m3tools
        for i in dimensions_keys:
                if i == 'VAR': size = novars
                elif i == 'TSTEP': size = None
                elif i == 'DATE-TIME': size = 2
                elif i == 'nv': continue
                elif i == 'LAY':
                   if (lsurf):
                     size = 1
                   else:
                     size = len(fin.dimensions['LAY'])
                else: 
                   try: size = len(fin.dimensions[i])
                   except: 
                      if i == 'LAY': 
                         if (lsurf):
                           size = 1
                         else:
                           size = len(fin.dimensions['nz'])
                      if i == 'VAR': size = len(fin.variables)
                      if i == 'ROW': size = len(fin.dimensions['ny'])
                      if i == 'COL': size = len(fin.dimensions['nx'])
                fout.createDimension(i,size=size)

        #copy global attributes
        attribs = "IOAPI_VERSION EXEC_ID FTYPE CDATE CTIME WDATE WTIME SDATE STIME TSTEP NTHIK NCOLS NROWS NLAYS NVARS GDTYP P_ALP P_BET P_GAM XCENT YCENT XORIG YORIG XCELL YCELL VGTYP VGTOP VGLVLS GDNAM UPNAM VAR-LIST FILEDESC HISTORY".split() # These attributes must be in the file to be used by m3tools
        cdate = int(datetime.date.today().strftime("%Y%j"))
        ctime = int(datetime.datetime.now().strftime("%H%M%S"))
        for i in attribs:
                try: val = getattr(fin,i)
                except: val = ""
                if 'numpy.float32' in str(type(val)):
                   val = val.item()
                if i == 'IOAPI_VERSION': val = "$Id: @(#) ioapi library version 3.1 $                                           "
                if i == 'EXEC_ID': val = "????????????????                                                                "
                if i == 'CDATE': val = cdate
                if i == 'CTIME': val = ctime
                if i == 'WDATE': val = cdate
                if i == 'WTIME': val = ctime
                if i == 'NTHIK': val = 1 # hard-coded, 2/17/2017,jjung
                if i == 'NLAYS':
                   if (lsurf):
                     val = 1
                   else:
                     val = novars
                if i == 'NVARS': val = novars
                if i == 'VGTYP': val = -9999
                if i == 'VAR-LIST': val = ''
                fout.setncattr(i,val)
        del fin
        fout.close()

def main():
    lsurf = False
    try :
      surflag  = os.environ['SURFACE_LAYER_ONLY']
    except :
      surflag  = 'F'
    if (surflag == 'T') or (surflag == 't') or (surflag == 'Y') or (surflag == 'y') :
       lsurf = True
    print "Output only surface?",lsurf
    outfile  = str(sys.argv[1])
    comb     = str(sys.argv[2])
    nifiles  = int(sys.argv[3]) # no. of input files
    infile = []
    for ifile in range(0,nifiles):
      infile.append(str(sys.argv[4+ifile]))
    
    print 'no. of input files =',nifiles
    fin = []
    for ifile in range(0,nifiles):
      try :
          fin.append(uamiv(infile[ifile]))
          if ifile == 0 : ftype = 'uam'
      except :
          fin.append(ncdf4.Dataset(infile[ifile]))
          if ifile == 0 : ftype = 'netcdf'
    
    NAME   = r'(?P<NAME>[a-zA-Z_][a-zA-Z_0-9\[\]]*)'
    ovar=[]
    ovarunit=[]
    formula=[]
    index = 0 # line no. of species def csv file
    with open(comb, 'rb') as csvfile:
        lines = csv.reader(csvfile, delimiter=',', quotechar='|')
        novars = sum(1 for row in lines if not ((''.join(row).strip() == '') or (row[0][0] == '/') or (row[0][0] == '#'))) # no. of output variables
        csvfile.seek(0)
        lnew = False
        if not os.path.exists(outfile): lnew = True
        if lnew: blank_file(infile[0], ftype, outfile, novars, lsurf)
        fout = ncdf4.Dataset(outfile,'a','r+',format="NETCDF3_CLASSIC")
        if lnew: 
           try: fout.createVariable('TFLAG',fin[0].variables['TFLAG'].dtype,fin[0].variables['TFLAG'].dimensions)
           except: fout.createVariable('TFLAG',('int32'),(u'TSTEP', u'VAR', u'DATE-TIME'))
        if lnew: fout.variables['TFLAG'].setncattr("units","<YYYYDDD,HHMMSS>")
        if lnew: fout.variables['TFLAG'].setncattr("long_name","TFLAG")
        if lnew: fout.variables['TFLAG'].setncattr("var_desc","Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS                                ")
        start = 0
        if not lnew: 
            #start = fout.variables["TFLAG"][:,0,:].shape[0]
            start = (datetime.datetime.strptime(str(getattr(fin[0],'SDATE')),"%Y%j")-datetime.datetime.strptime(str(getattr(fout,'SDATE')),"%Y%j")).days*240000/getattr(fin[0],'TSTEP') 
        try: end = start + fin[0].variables["TFLAG"][:,0,:].shape[0]
        except: end = start + len(fin[0].dimensions['nt'])
    
        #generate TFLAG arrays
        try: idate = getattr(fin[0],'SDATE')
        except: idate = 2011001 # random value
        try: itime = getattr(fin[0],'STIME')
        except: itime = 0 # random value
        try: tstep = getattr(fin[0],'TSTEP')
        except: tstep = 10000 # random value
        for istep in range(start,end):
                for ivar in range(novars):
                        fout.variables['TFLAG'][istep,ivar,0]=idate
                        fout.variables['TFLAG'][istep,ivar,1]=itime
                itime += tstep
                if itime == 240000:
                        itime = 0
                        idate = int((datetime.datetime.strptime(str(idate),"%Y%j") + datetime.timedelta(days=1)).strftime("%Y%j"))
    
        ntstamps = len(fin[0].dimensions['TSTEP']) #inf1 no. of time stamps
        lines = csv.reader(csvfile, delimiter=',', quotechar='|')
        for line in lines:
            if ''.join(line).strip() == '': continue # skip blank line
            if (line[0][0] == '/') or (line[0][0] == '#'): continue # skip the lines starting with /, #, or blank
            ovar.append(line[0].split()[0])
            ovarunit.append(line[1].split()[0])
            formula.append(line[2].split()[0])
    
            if lnew: fout.createVariable(ovar[index],'f',('TSTEP', 'LAY', 'ROW', 'COL'))
            if lnew: fout.variables[ovar[index]].setncattr("units",ovarunit[index])
            if lnew: fout.variables[ovar[index]].setncattr("long_name",'{0:<16}'.format(ovar[index]))
            if lnew: fout.variables[ovar[index]].setncattr("var_desc",'{0:<80}'.format(ovar[index]))
            p = re.compile(NAME) # declare pattern match that include alphabet, number, [ or ]
            vars = p.findall(formula[index]) # find continuous blocks of p defined above
            varname=[]
            fins=[]
            for var in vars:
              i = vars.index(var)
              varname.append(re.findall(r"\w+",var)[0]) # delimit by [ or ] and store the first element to varname by appending, Let's assume your varname[0] = NO_DD for the explanation of next next line
              fins.append(int(re.findall(r"\w+",var)[1])) # delimit by [ or ] and store the second element to varname by appending, Let's assume your fins[0] = 1 for the explantion of next line
              if fins[i] < 0:
                print 'File index is negative!', fins[i]
                exit()
              elif fins[i] == 0:
                if (lsurf):
                  exec("".join([varname[i],"_",str(fins[i]), "= fout.variables[varname[i]][start:end,0,:,:]"])) # if spec.def file call [0], use a variable that is already calculated.
                else:
                  exec("".join([varname[i],"_",str(fins[i]), "= fout.variables[varname[i]][start:end,:,:,:]"])) # if spec.def file call [0], use a variable that is already calculated.
              elif fins[i] <= nifiles:
                if (lsurf):
                  exec("".join([varname[i],"_",str(fins[i]), "= fin[int(fins[i])-1].variables[varname[i]][0:ntstamps,0,:,:]"])) # execute such a line, NO_DD_1 = fin.variables[NO_DD][0:24,:,:]
                else:
                  exec("".join([varname[i],"_",str(fins[i]), "= fin[int(fins[i])-1].variables[varname[i]][0:ntstamps,:,:,:]"])) # execute such a line, NO_DD_1 = fin.variables[NO_DD][0:24,:,:]
              else:
                print 'File index is larger than no. of input files!', fins[i]
                print 'no. of input files', nifiles
                exit()
            for i in range(0,nifiles+1): # replace [] to _. (e.g. NO_DD[1] -> NO_DD_1)
                formula[index] = formula[index].replace("".join(["[",str(i),"]"]),"".join(["_",str(i)])) # change formula expression such as 0.014*(NO_DD[1]+NO_DD[1]) to 0.014*(NO_DD_1+NO_DD_1) as we changed the experssions by removing [] and replace with _.
            dict_vars={}
            vars = p.findall(formula[index]) # return all the variables in formula
            for var in vars:
              exec("".join(["dict_vars['",var,"']=",var]))
            e = ExpressionEvaluator(dict_vars) # generate class e. To declare variables in dic_vars, dic_vars is passed as an argument.
            if (lsurf):
              fout.variables[ovar[index]][start:end,0,:,:] = e.parse(formula[index]) #evalutae formular
            else:
              fout.variables[ovar[index]][start:end,:,:,:] = e.parse(formula[index]) #evalutae formular
            index += 1 
    
        fout.setncattr('VAR-LIST',''.join(map(lambda x: '{0:<16}'.format(x),ovar)))
        fout.close()

if __name__ == '__main__':
    main()
