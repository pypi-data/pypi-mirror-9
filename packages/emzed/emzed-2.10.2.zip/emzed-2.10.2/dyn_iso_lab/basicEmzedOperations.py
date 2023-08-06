# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:46:32 2012

@author: pkiefer
"""
import emzed
import re
#import ms
import emzed.mass as mass
import emzed.adducts as adducts
defaultDirectory = "//gram/omics/gr_vorholt"
from emzed.core.data_types import PeakMap, Table
import time
import emzed.elements as elements
# Table operations


def _deltaIsotope(isotope):
#    import elements
    """ calculates mass difference between  selected "isotope" and light isotope
    """
    element=re.split("[0-9]", isotope)[0]
    return eval("elements."+isotope+".mass")-eval("elements."+element+".m0")

def peakmap2Table(pMap):

    """Converts peakmap into table format containing TIC over comlete time and
       mass range.
    """
    #pMap=ms.loadPeakMap(name)
    table=emzed.utils.toTable("filename", [pMap.meta.get("source")])
    table.title=pMap.meta.get("full_source")
    table.addColumn("rtmin", 0.0, format_="'%.2fm' %(o/60.0)")
    table.addColumn("rtmax", pMap.allRts()[-1])
    table.addColumn("mzmin", float(pMap.mzRange()[0]))
    table.addColumn("mzmax", float(pMap.mzRange()[1]))
    table.addColumn("peakmap", pMap)
    return table

def adductTable(peakmap):
    """ determines ion polarity from peakmap.  If not return value is None 
    """
    polarity=peakmap.polarity
            
    assert polarity in "+-", "polarity is not properly defined"
    if polarity=="+":
           adductTable=adducts.positive.buildTableFromUserDialog()

    if polarity=="-":
            adductTable=adducts.negative.buildTableFromUserDialog()

    return adductTable

def adductsDialog(items):
    """ determines ion polarity from a list of peakmaps or peakmap(s) attached 
        to a list of tablea. If polarity is unique function opens dialog to 
        choose possible adducts. If not return is None 
    """
    assert len(items), "need nonempty list as input"
    # check data type consistency
    is_peakmaps = all( [isinstance(t, PeakMap) for t in items])
    is_tables = all([isinstance(t, Table) for t in items])

    if not is_peakmaps and not is_tables:
        assert False, "need either peakmaps or tables as input"

    # create adducts
    if is_peakmaps:
        peakmaps=items
    else:
        peakmaps=[]
        for t in items:
            postfixes=t.supportedPostfixes(["peakmap"])
            for pstfx in postfixes:
                peakmaps.extend(list(set(t.getColumn("peakmap"+pstfx).values)))
                
    # check if polarity of peakmaps in chosen tables is consistent
    polarity_control=uniquePolarityCheck(peakmaps)
    if polarity_control:
       adducts=adductTable(peakmaps[0])
    else:
        emzed.gui.showWarning("Ionisation polarity of choosen items not consistent!!"\
                        "\ Please chose adducts for both polarities!")
        adducts=adducts.all.buildTableFromUserDialog()
    return adducts

def getPolarity(items):
    polarity=[]
    check=[isinstance(item, Table) for item in items]
    print check
    assert len(set(check))<=1, "More than 1 object type in item list"
    if check[0]:
        polarity=[]
        for t in items:
            postfixes=t.supportedPostfixes(["peakmap"])
            for postfix in postfixes:
                peakmap="peakmap"+postfix
                peakmaps=list(set(t.getColumn(peakmap).values))
                polarity.extend([pm.polarity for pm in peakmaps])
    check=[isinstance(item, PeakMap) for item in items]
    print check
    assert len(set(check))<=1, "More than 1 type in item list"
    if check[0]:
        polarity=[pm.polarity for pm in items]
    
    if polarity:
        assert len(set(polarity))==1, "polarity in peakmap not unique"
        return polarity[0]
    else: 
        assert True, "Item list is neither of type PeakMap nor of type Table"
    

def _getAdducts(polarity, title):

     if polarity=="+":
         all_adducts=adducts.positive.toTable()
         chosen=adducts.positive.createMultipleChoice(title).show()
     if polarity=="-":
        all_adducts=adducts.negative.toTable()
        chosen=adducts.negative.createMultipleChoice(title).show()
     all_adducts.addEnumeration()
     selected=all_adducts.filter(all_adducts.id.isIn(chosen))
     selected.dropColumns("id")
     return selected


def _addMzValues(table,polarity):

    mode=emzed.gui.DialogBuilder("how to get mz values")\
    .addBool("individual adducts for each compound", default=True)\
    .show()

    if mode:
        compounds=table.splitBy("name")
        cal_list=[]
        for compound in compounds:
            title=emzed.gui.DialogBuilder(compound.name.uniqueValue()+\
                                    ": choose adducts ")
            adduct=_getAdducts(polarity, title)
            cal_list.append(massSolutionSpace(compound, adduct))
        result=emzed.utils.mergeTables(cal_list)
#        result.renameColumns(mzTheo="mz")

    else:

        if polarity=="+":
            adduct=adducts.positive.buildTableFromUserDialog()
        if polarity=="-":
            adduct=adducts.negative.buildTableFromUserDialog()
        result=massSolutionSpace(table, adduct)
    result.info()
    return result


def massSolutionSpace(sTab, adductTable):
    """ Function calculates m/z values (solution space) from compound tables
        with column mass by joining with adduct table ; in case column
        <mass> is missing values are calculated from column "mf"

    """
    mass_pstfx=sTab.supportedPostfixes(["mass"])
    assert len(mass_pstfx)<=1 , ("column 'mass' is not unique")
    if mass_pstfx:
        mass_pstfx=mass_pstfx[0]
        mass_col="mass"+mass_pstfx
    else:
        mf_pstfx=sTab.supportedPostfixes(["mf"])
        assert len(mf_pstfx)==1, ("column 'mf' is missing or not unique")
        mf_pstfx=mf_pstfx[0]
        col_mf="mf"+mf_pstfx
        assert sTab.hasColumn(col_mf),\
                ("column mf is missing!")
        sTab.addColumn("mass"+mf_pstfx, sTab.mf.apply(mass.of))
        mass_col="mass"+mf_pstfx
    sTab=sTab.join(adductTable,True)
    postfix=sTab.supportedPostfixes(["mass_shift", "z"])
    assert len(postfix)==1, ("columns mass_shift and/or z are not unique: check Tables!")
    postfix=postfix[0]
    shift="mass_shift"+postfix
    charge="z"+postfix
    sTab.addColumn("mzTheo", (sTab.getColumn(mass_col) + \
                    sTab.getColumn(shift))/sTab.getColumn(charge),\
                    insertBefore="mass")
    sTab.dropColumns("z_signed"+postfix)
    sTab.renameColumns(**{charge:"z", shift:"mass_shift",
                          "adduct_name"+postfix:"adduct"})
    if mass_col!="mass":
        sTab.renameColumns(**{mass_col:"mass"})
    return sTab

###################################################################################
# mz peak detectors



def checkColnames(required, table):
    """ Checks whether colNames in list 'required' are present in table
    """
    assert isinstance(required, list)
    print required
    supportedPostfixes = table.supportedPostfixes(required)
    if not supportedPostfixes:
        missing=set(required)-set([name for name in table.getColNames()])
        raise Exception("required column(s) %s are missing" % missing)



def defineMzPeaks(sTab,peakmap, mzTol):
    """ creates table from peakmap containing mzPeaks defined in sTab. Required
        colNames are "rtmin","rtmax","mzTheo".
    """
    
    required=["mzTheo","rtmin","rtmax"]
    try:
        checkColnames(required, sTab)
    except:
        required=["mzmin", "mzmax", "rtmin","rtmax"]
    supportedPostfixes=sTab.supportedPostfixes(required)
    for pstfx in supportedPostfixes:
         sTab.updateColumn("peakmap"+pstfx, peakmap)
         sTab.updateColumn("mzmin"+pstfx, sTab.getColumn("mzTheo"+pstfx)-mzTol, format_="%.5f")
         sTab.updateColumn("mzmax"+pstfx, sTab.getColumn("mzTheo"+pstfx)+mzTol, format_="%.5f")
         # update format of rtmin and rtmax
         sTab.updateColumn("rtmin"+pstfx, sTab.getColumn("rtmin"+pstfx),
                              format_="'%.2fm' %(o/60.0)")
         sTab.updateColumn("rtmax"+pstfx, sTab.getColumn("rtmax"+pstfx),
                              format_="'%.2fm' %(o/60.0)")


def extractPeakParametersByIntegration(peaks, int_mode):
    """ extracts peak parameters mz, and rt by integration of table peaks. required
        colNames: "rtmin", "rtmax", "mzmin", "mzmax", peakmap
    """
    peaks=emzed.utils.integrate(peaks, int_mode)
    required=["rtmin", "rtmax", "mzmin", "mzmax", "peakmap"]
    checkColnames(required, peaks)
    supportedPostfixes=peaks.supportedPostfixes(required)
    for pstfx in supportedPostfixes:
        # calculate RT and mz columns
        peaks.addColumn("mz"+pstfx,None, insertBefore="mzmin",\
                     type_=float, format_="%.5f")
        if int_mode=="emg_exact":
            peaks.updateColumn("rt"+pstfx, peaks.getColumn("params"\
                                 +pstfx).apply(lambda p: p[1]),format_="%.2f")
        else:
            peaks.updateColumn("rt"+pstfx, (peaks.rtmin+peaks.rtmax)/2.0)
    emzed.utils.recalculateMzPeaks(peaks)
    return peaks

def peakAreaDetector(sTab,fTab,mzTol, int_mode="no_integration", 
                     removeRedundance=False):
    """ function detects peak from parameter table with column mzmin,
        mzmax, rtmin, rtmax. Input file is output of function peakmap2Table
    """
     # join sTab with fTab
    peaks=sTab.leftJoin(fTab, True)
    peaks.replaceColumn("mzmin__0", peaks.mzTheo-mzTol)
    peaks.replaceColumn("mzmax__0", peaks.mzTheo+mzTol)
    if peaks.hasColumns('rtmin', 'rtmax'):
        peaks.replaceColumn("rtmin__0", peaks.rtmin)
        peaks.replaceColumn("rtmax__0", peaks.rtmax)
#        peaks.dropColumns('rtmin__0', 'rtmax__0')
#        peaks.info()
        
    #peaks.replaceColumn("peakmap__0", fTab.peakmap.uniqueNotNone())
    #peaks.replaceColumn("source__0", fTab.source.uniqueNotNone())
    peaks=emzed.utils.integrate(peaks, int_mode)
#    peaks.addColumn("mz__0", peaks.mzTheo, insertBefore="mzmin__0")
    #ms.inspect(peaks)
    #ms.recalculateMzPeaks(peaks)
    removePostfixesAndRedundance(peaks, removeRedundance=removeRedundance)
    return peaks



def uniquePolarityCheck(peakmaps):
    """check consistency of loaded items (PeakMaps or Tables) regarding polarity
    """
    
    assert len(peakmaps)>0, "no peakmaps in list"
    polarities=[peakmap.polarity for peakmap in peakmaps]
    return len(set(polarities)) == 1

def _normalize_mf(mf):
    """Alphabetic order of elements in MF: 
    """
    import re
    fields = re.findall("([A-Z][a-z]?)(\d*)", mf)
    # -> z.b [ (Ag, ""), ("Na", "2")]
    fields.sort()
    normalized = [ sym + ("1" if count=="" else count) for (sym, count) in fields ]
    # -> ["Ag1", "Na2" ]
    return "".join(normalized)
    
def uniqueIdTab(table,colName):
    """uniqueIdTab(table,colName): removes all rows with redundand entries in column colName from table"""
    unique=[]
    table = table.copy()
    if colName=="mf":
        table.addColumn("mf_normalized", table.mf.apply(_normalize_mf))    
        tables_by_colN = table.splitBy("mf_normalized")
    else:
        tables_by_colN=table.splitBy(colName)
        
    for t in tables_by_colN:
        t.addEnumeration("_id")
        t = t.filter(t._id == t._id.min)
        t.dropColumns("_id")
        unique.append(t)
    if len(unique)>0:
        return emzed.utils.mergeTables(unique)
    else:
        return table

#################################################################################


def compTables(tabL):
    """compTables(tabL) creates a list of detected over all tables and joines tables
        to a single table to enhance result comparison
    """
    for t in tabL:
        #t=uniqueIdTab(t,"id")
        pass

    a=emzed.utils.mergeTables(tabL)
    #a=a.filter(a.dM0==0.0)
    nameL=a.splitBy("name")
    allList=[]
    for t in nameL:
        rtL=t.splitBy("rt")
        mergeL=[]
        mergeL.append(rtL[0])
        for i in range(1,len(rtL)):
            x=mergeL[-1]
            rtvalue=x.rt.values[0]
            y=rtL[i]
            add=y.filter(~y.rt.inRange(rtvalue-90.0,rtvalue+90.0))
            if add:
                mergeL.append(add)
        allList.extend(mergeL)

    allComp=emzed.utils.mergeTables(allList)
    allComp=allComp.extractColumns("name","mf","rt")
    allComp.addColumn("m0Calc", allComp.mf.apply(mass.of))

    for i in range(len(tabL)):
        t=tabL[i]
        t.addColumn("deltaM",(t.mz-(t.mf.apply(mass.of)+t.adductMz))*1000,format_="%.2f MMU")
        t=t.filter(t.deltaM.apply(lambda v: abs(v))<=1)

        allComp=allComp.leftJoin(t,allComp.m0Calc.approxEqual(t.mz-t.adductMz,1*emzed.MMU)\
             &allComp.rt.approxEqual(t.rt,50) & (allComp.name==t.name))
        methcolname = "method__%d" % i
        #print allComp.colNames

        allComp.replaceColumn(methcolname, allComp.getColumn(methcolname).ifNotNoneElse("no_integration"))
    return allComp

def removePostfixesAndRedundance(t, removeRedundance=True):
    """ in place: all redundant columns as well as unnecessary postfixes 
        of table t are removed
    """
    postfixes=t.findPostfixes()
    postfixes.remove("")
    
    with_pstfx=[]
    colnames = [name for name in t.getColNames()]
    for fix in postfixes:
        names=[name.split(fix)[0] for name in t.getColNames() if name.endswith(fix)]
        with_pstfx.extend(names)
    double=set(colnames).intersection(set(with_pstfx))
    
    unique=set(with_pstfx).difference(set(colnames))
    if removeRedundance:
        for colname in double:
            for fix in postfixes:
                if t.hasColumn(colname+fix):
                    if t.getType(colname) is object or t.getType(colname+fix) is object:
                        expr = t.getColumn(colname).apply(id) == t.getColumn(colname+fix).apply(id)
                    else:
                        expr = t.getColumn(colname) == t.getColumn(colname+fix)
                    check=t.filter(expr)
                    if len(check)==len(t):
                        t.dropColumns(colname+fix)
    for colname in unique:
        for fix in postfixes:
            if t.hasColumn(colname+fix):
                t.renameColumns(**{colname+fix:colname})

def cleanUpCentwaveTable(t):
    """ removes peak splitting caused by Centwave peak detector
    """
    rtmin_list=[]
    rtmax_list=[]
    mzmin_list=[]
    mzmax_list=[]
    id_list=[]
    id_=0
    t.updateColumn("mz_bin", t.mz.apply(lambda mz: str(int(mz*1000))))
    subts = t.splitBy("mz_bin")
    for subt in subts:
        subt.sortBy("rt")
        if len(subt)>1:

            rtmaxs=subt.rtmax.values
            rtmaxs=rtmaxs[:-1]
            rtmins=subt.rtmin.values
            rtmins=rtmins[1:]
            delta=[rtmins[i]-rtmaxs[i] for i,_ in enumerate(rtmins)]
#            return delta
            delta.append(0.0)
            print delta
            splitter=[]
            i=0
            for v in delta:
                if v>120:
                    i=i+1
                    splitter.append(str(i))
                    subt.addColumn("_splitter",splitter)
                    peaks=subt.splitBy("_splitter")
                    print
                    print splitter

            for peak in peaks:

                rtmin_list.append(peak.rtmin.min())
                rtmax_list.append(peak.rtmax.max())
                mzmin_list.append(peak.mzmin.min())
                mzmax_list.append(peak.mzmax.max())
                id_list.append(id_)
                id_=id_+1

        else:
            rtmin_list.append(subt.rtmin.uniqueValue())
            rtmax_list.append(subt.rtmax.uniqueValue())
            mzmin_list.append(subt.mzmin.uniqueValue())
            mzmax_list.append(subt.mzmax.uniqueValue())
            id_list.append(id_)
            id_=id_+1

    cleaned=emzed.utils.toTable("id", id_list)
    cleaned.addColumn("rtmin", rtmin_list, format_="'%.2fm' %(o/60.0)")
    cleaned.addColumn("rtmax", rtmax_list, format_="'%.2fm' %(o/60.0)")
    cleaned.addColumn("mzmin", mzmin_list, format_="%.5f")
    cleaned.addColumn("mzmax", mzmax_list, format_="%.5f")
    cleaned.addColumn("peakmap", t.peakmap.uniqueValue())
    cleaned=extractPeakParametersByIntegration(cleaned, "emg_exact")
    return cleaned

###########################################################################
# enhances integration algorithm

def _reintegrate_emg_enlarge(t, enlarge=0.2):
    """
    """
    expr=t.getColumn                        
    t.updateColumn("rtmin", expr("rtmin")-(expr("rtmax")-expr("rtmin"))*enlarge)
    t.updateColumn("rtmax", expr("rtmax")+(expr("rtmax")-expr("rtmin"))*enlarge)
    integrated=emzed.utils.integrate(t, "emg_exact")
    expr=integrated.getColumn                        
#    integrated.updateColumn("rt", integrated.params.apply(lambda p: p[1]) )
    integrated.updateColumn("area", expr("area")*1.0, format_="%2.2e")
    integrated.updateColumn("rmse", expr("rmse")*1.0, format_="%2.2e")
    
    return integrated
    
def _integration(t):
    good=[]
    
    t1=t.copy()
    t1_int=emzed.utils.integrate(t1, "trapez")
    t1_int==t1_int.extractColumns("peak_no", "method", "area")
    t_int=emzed.utils.integrate(t, "emg_exact")
    comp=t_int.join(t1_int, t_int.peak_no==t1_int.peak_no)
    comp.addColumn("fold_change", (comp.area+1.0)/(comp.area__0+1))
    critical=comp.filter(~comp.fold_change.inRange(0.67,1.5))
    id_bad=critical.peak_no.values
    ok=t_int.filter(~t_int.peak_no.isIn(id_bad))
    id_ok=ok.peak_no.values
    print
    print "good integration", len(ok)
    bad=t_int.filter(t_int.peak_no.isIn(id_bad))
    if len(ok):
        good.append(ok)
    count=0
    while len(bad)>0:
        bad=_reintegrate_emg_enlarge(bad)
        comp=bad.join(t1_int, bad.peak_no==t1_int.peak_no)
        comp.addColumn("fold_change", (comp.area+1.0)/(comp.area__0+1))
        critical=comp.filter(~comp.fold_change.inRange(0.67,1.5))
        print 
        print "number of critical: ", len(critical.peak_no.values)
        id_bad=critical.peak_no.values
        id_ok=list(set(comp.peak_no.values).difference(set(id_bad)))
        ok=bad.filter(bad.peak_no.isIn(id_ok))
        
        bad=bad.filter(bad.peak_no.isIn(id_bad))
        
        if len(ok):
            good.append(ok)
        count=count+1
        if count>3:
            if len(bad):
                bad=emzed.utils.integrate(bad, "trapez")
                good.append(bad)
            break
    
    if len(good)>1:
        return emzed.utils.mergeTables(good, force_merge=True)
    elif len(good)==1:
        return good[0]
   
def _updateIntegration(t, integrated, postfix):
    """
    """
    
    combine=t.join(integrated, t.peak_no==integrated.peak_no)
    colnames=[name for name in integrated.getColNames() if name!="peak_no"]
    pstfx=combine.supportedPostfixes(colnames)[-1]
    combine.dropColumns("peak_no"+pstfx)
    for name in colnames:
        combine.renameColumns(**{name+pstfx:name+postfix})
    return combine

def _getColumns(t ,postfix):
    """
    """
    table_type_col=[["peak_no", "rt","rtmin", "rtmax", "mzmin", "mzmax",
                      "peakmap"],
                    ["method", "area", "rmse", "params"],
                    ["fwhm"]]
    colnames=[name for name in t.getColNames() if name.endswith(postfix)]
    if postfix:
        bas_names=set([name.split(postfix)[0] for name in colnames])
    else:
        bas_names=colnames
    drop_col=[]
    for types in table_type_col:
        if not len(set(types).difference(bas_names)):
            drop_col.extend(types)
    extract_col=[name+postfix for name in drop_col]
    drop_col.remove("peak_no")
    return extract_col, drop_col
     
    
def enhancedIntegrate(tt):
    """
    """
    
    t=tt.copy()
    # add internal line identifier which is not in conflict with id
    
    t.addColumn("peak_no", range(len(t)))
    
        
    required=["rt","rtmin", "rtmax", "mzmin", "mzmax"]
    postfixes=t.supportedPostfixes(required)
    
    for postfix in postfixes:
        extract_col, remove_col=_getColumns(t, postfix)
        rt="rt"+postfix
        rtmin="rtmin"+postfix
        rtmax="rtmax"+postfix
        fwhm="fwhm"+postfix
        
        if t.hasColumn("fwhm"+postfix):
            expr=t.getColumn
            t.replaceColumn(rtmin, expr(rt)-expr(fwhm)/2.0)
            t.replaceColumn(rtmax, expr(rt)+expr(fwhm)/2.0)
        
        
        integrated=t.extractColumns(*extract_col)
        
        t.dropColumns(*remove_col)
        for name in extract_col:
            if postfix:
                integrated.renameColumns(**{name+postfix:name})
        integrated=_integration(integrated)

        t=_updateIntegration(t, integrated, postfix)
    fixes=t.supportedPostfixes(["peak_no"])
    for fix in fixes:
        name="peak_no"+fix
        t.dropColumns(name)
    return t
    
    
    
def timeFormats(table, colnames):
    """ Sets table formats of colnames to minutes
    """
    assert table.hasColumns(*colnames), "cot all column names in table %s" %table.title
    supportedPostfixes=table.supportedPostfixes(colnames)
    for postfix in supportedPostfixes:
        for name in colnames:
            colName=name+postfix
            table.replaceColumn(colName, table.getColumn(colName),
                                format_="'%.2fm' %(o/60.0)",type_=float)


def timeLabel():
    """gives string of current time back. can be used e.g. to label filenames
    """
    x=time.localtime()
    label="_"+str(x.tm_year)+"_"+str(x.tm_mon)+"_"+str(x.tm_mday)+"_"+str(x.tm_hour)+"h"\
           + str(x.tm_min)+"m"+str(x.tm_sec)+"s"
    return label