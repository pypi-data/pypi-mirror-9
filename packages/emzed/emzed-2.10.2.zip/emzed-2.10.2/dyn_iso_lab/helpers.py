# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 16:04:22 2012

@author: pkiefer & uschmitt
"""
import emzed
import os
import time
import emzed.mass as mass
from emzed.core.data_types import Table

#############################################################################   
def batchPeakmaps():
    """loads a set of peakmaps into workspace  and converts them into tables"""
    fileList=emzed.gui.askForMultipleFiles()
    if fileList[0]==None:
       return []
    tList=[]
    for name in fileList:
        pMap=emzed.io.loadPeakMap(name)
        table=emzed.utils.toTable("filename", [pMap.meta.get("source")])
        table.title=pMap.meta.get("full_source")
        table.addColumn("rtmin", 0)
        table.addColumn("rtmax", pMap.allRts()[-1])
        table.addColumn("mzmin", float(pMap.mzRange()[0]))
        table.addColumn("mzmax", float(pMap.mzRange()[1]))
        table.addColumn("peakmap", pMap)
        tList.append(table)
    return tList
    
    
def batchTables():
    """loads a set of tables into workspace"""
    fileList=emzed.gui.askForMultipleFiles(extensions=["table"])
    if fileList[0]==None:
       return []
    tList=[]
    for name in fileList:
        table=emzed.io.loadTable(name)
        tList.append(table)
    return tList
    

   
def buildSampleInfo(path):
     """ Builds default sampleInfo File for idmsQuanTool from mzXML file 
         name list
     """
     nameL=emzed.gui.askForMultipleFiles(startAt=path, extensions=["mzXML"])
     sName=[os.path.split(name)[1] for name in nameL]
     dlg = emzed.gui.DialogBuilder("Column Settings for Sample Info Parameters")\
             .addFloat("cell extract volume uL",default=1.0, \
             help="enter the volume of natural labeled extract in sample [uL]")\
             .addFloat("internal standard volume uL",default=1.0, \
             help="enter the volume of internals standard added to sample [uL]")\
             .addFloat("biomass concentration",default=1.0, \
             help="enter the volume of internals standard added to sample [units/L]")\
             .addString("unit of biomass concentration", default="(g CDW)/L")\
           
     vol_sample, vol_int_std, biomass_conc, conc_unit, = dlg.show()
     
     sInfo=emzed.utils.toTable("sampleFileName", sName)
     sInfo.addColumn("V_sample", vol_sample, format="%.2f uL")
     sInfo.addColumn("V_intStd", vol_int_std, format="%.2f uL")
     # string interpolation renders %% to %, so we build a format string
     # as follows, results in a format string like '%.2f ml':
     fmt_with_unit = "%%.2f %s" % conc_unit
     sInfo.addColumn("cCells", biomass_conc, format=fmt_with_unit)
     emzed.gui.inspect(sInfo)
     return sInfo
     
def buildQuanTable(numRows):
    """Builds a Quantification table with numRows rows and the default column
        titles"""
    nameL=[]
    for i in range(numRows):
        nameL.append("name")
    QuanT=emzed.utils.toTable("name", nameL)
    QuanT.addColumn("mf", "CHNOPS")
    QuanT.addColumn("rtmin",5*60,format="'%.2fm' %(o/60.0)")
    QuanT.addColumn("rtmax",45*60,format="'%.2fm' %(o/60.0)")
    emzed.gui.showInformation("please correct column entries. The monoisotopic mass is calculated from mf")
    emzed.gui.inspect(QuanT)
    QuanT.addColumn("m0", QuanT.mf.apply(mass.of))
    return QuanT
    

def collectSourceTables(t):
    
    """ Extracts source tables from joined tables (by u. schmitt)
        Example: if c=a.join(b, a.ColName==b.ColName)
                collect_source_table(c) returns
                [a,b]
    """    
    result = []
    for source in t.meta:
        if isinstance(source, Table):
            result.append(source)
            result.extend(collectSourceTables(source))
            
    return result
    
# handling of temporary result files during batches, works only in project context !!!
def saveTempDir(table, path):
    """ creates _temp directory during batch processing of a table list. 
     in case of joined table make sure that meta Data are from a single table  
    """
    target_path=os.path.join(path)
    if os.path.exists(target_path)==False:
           os.mkdir(target_path)
    #get all exisiting filenames in path    
    if table.colNames.count("__")==1:
        tabSources=collectSourceTables(table)
    else:
        tabSources=[]
    if table in tabSources or table.meta.has_key("loaded_from"):
        name=table.meta["loaded_from"]
        name=name.encode("latin-1")
        if os.path.exists(name):
            path=os.path.split(name)[0]
            baseN=os.path.basename(name)
    else:
        baseN="_temp"+table.title
    store_path=os.path.join(target_path,baseN)
    if os.path.exists(store_path):
        print "WARNING %s file already in temp file" %table.title
        return
    table.store(store_path)

    
def checkTempDir(table):
    
    if table.colNames.count("__")==1:
        tabSources=collectSourceTables(table)
    else:
        tabSources=[]
    if table in tabSources or table.meta.has_key("loaded_from"):
        name=table.meta["loaded_from"]
        name=name.encode("latin-1")
        if os.path.exists(name):
            path=os.path.split(name)[0]
            baseN=os.path.basename(name)
            target_path=os.path.join(path,"_temp")
            if os.path.exists(target_path):
                target_path=os.path.join(target_path,baseN)
            os.mkdir(target_path) 
            return True, target_path
        
        else:
            emzed.gui.showWarning("There is a problem with table meta data")
            return False, []

def remTempDir(path):
    
     target_path=os.path.join(path)
     if os.path.exists(target_path):
         os.removedirs(target_path)
         
 ################################################################
def buttonChoiceDialog(*options):
    """ Example: i=buttonChoiceDialog("a","b","c") 
        Creates button dialog with Buttons, a,b, and c. 
        Return value is index of chosen button: 
        When choosing "b" return value is 1.
    """
    result = dict(res=-1)
    b = emzed.gui.DialogBuilder()
    b.addString("current_choice")
    def record(idx):
        def callback(inst):
            inst.current_choice = options[idx]
            result["res"] = idx
        return callback
    for i, option in enumerate(options):
        b.addButton(option, record(i))
    
    b.show()
    return result["res"]   
#############################################################################

def elementsInFormula(mf):
    """returns list of elements in string format formula mf
    """
    f=emzed.utils.formula(mf)
    return [element for (element, isotope) in f.asDict().keys()]

def timeLabel():
    """ gives string of current time back.  can be used e.g. to label filenames
    """
    x=time.localtime()
    label="_"+str(x.tm_year)+str(x.tm_mon)+str(x.tm_mday)+"_"+str(x.tm_hour)+"h"\
           + str(x.tm_min)+"m"+str(x.tm_sec)+"s"
    return label


def dump_table_info_py(t):
    tconv = lambda t: str(t).split(" ")[1][1:-2]
    tuples = [(n, tconv(t)) for (n,t) in zip(t.getColNames(), t.getColTypes())]
    print tuples
    
def dump_types(fun):
    def wrapped(*args):
        for i, arg in enumerate(args):
            if isinstance(arg, Table):
                print "arg %d:" % i,
                dump_table_info_py(arg)
        result = fun(*args)
        if isinstance(result, Table):
            print "result=", 
            dump_table_info_py(result)
        elif isinstance(result, (list, tuple)):
            for i, res in enumerate(result):
                if isinstance(res, Table):
                    print "res %d:" % i,
                    dump_table_info_py(res)
        
    return wrapped
        
        

def _save(tables, path):
    
    for t in tables:
        name=str(t.mf.uniqueValue())+'.csv'
        target=os.path.join(path,name)
        print target
        emzed.io.storeCSV(t, target)










