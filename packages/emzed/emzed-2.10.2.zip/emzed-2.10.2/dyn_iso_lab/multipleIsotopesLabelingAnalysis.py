# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:17:27 2012

@author: pkiefer
"""
import os
import re
import emzed
import msProjects as basic
import basicEmzedOperations as basicOp
import parameterTableBuilder as buildPara
from emzed.core.data_types import Table
#import helpers

################################################################
# HELPER FUNCTIONS

def _multipleIsotopesSplitter(table):
    """ adds a temporary column to the table encoding the different
       isotopes by combining the number of isotopes with separator _
    """
    supported_pstfx=table.supportedPostfixes(["isotope", "num_isotopes"])
    table.addColumn("_sep", "_")
    table.updateColumn("_split", "")
    for i,pf in enumerate(supported_pstfx):
       if i+1<len(supported_pstfx):
           table.replaceColumn("_split", table._split+\
                               table.getColumn("num_isotopes"+pf).apply(str)\
                               + table._sep)
       else:
           table.replaceColumn("_split", table._split+\
                               table.getColumn("num_isotopes"+pf).apply(str))
    table.dropColumns("_sep")


def _resultFilter(table, min_mi):
    """ removes all istotopes with mass isotopomer fraction below.... for all
        samples measured to reduce plotting impact

    """
    filtered=[]
    _multipleIsotopesSplitter(table)
    compounds=table.splitBy("id")
    for compound in compounds:
            isotopomers=compound.splitBy("_split")
            for isotopomer in isotopomers:
                if isotopomer.mi_fraction.max()>min_mi:
                    filtered.append(isotopomer)
    return emzed.utils.mergeTables(filtered, force_merge=True)




def setUniqeColValueToTitle(tables, colname):
    """
    """
    modified_tables=[]
    for table in tables:
        table.title=table.getColumn(colname).uniqueValue()
        modified_tables.append(table)
    return modified_tables


def _getFileAndCompoundNames(result_table):
    filenames=["all"]
    filenames.extend([sample.source.uniqueValue() for sample in \
                    result_table.splitBy("source")])
    compoundnames=["all"]
    compoundnames.extend([compound.name.uniqueValue() for compound in\
                    result_table.splitBy("id")])
    return filenames, compoundnames


def _setPstfxToMi(table, colnames):
    """ Sets postfix of column to corresponding mass isotopomer
    """
    postfixes=table.supportedPostfixes(["area", "rmse"])
    isotope_ps=table.supportedPostfixes(["isotope", "num_isotopes"])
    for postfix in postfixes:
        mi_fix="_"
        selected_ps=[]
        for ps in isotope_ps:
            if ps.endswith(postfix):
                selected_ps.append(ps)
        for ps in selected_ps:
            col_0="isotope"+ps
            col_1="num_isotopes"+ps
            mi_fix=mi_fix+str(table.getColumn(col_0).uniqueNotNone())+"x"+\
                    str(table.getColumn(col_1).uniqueNotNone())

        for name in colnames:
                col_before=name +postfix
                col_after=name + mi_fix
                table.renameColumns(**{col_before:col_after})


def _deltaIsotope(isotope):
    """ calculates mass difference between  selected "isotope" and light isotope
    """
    element=re.split("[0-9]", isotope)[0]
    return eval("elements."+isotope+".mass")-eval("elements."+element+".m0")

def _rtMzDialog():
        rtTol, mzTol=emzed.gui.DialogBuilder("Quan Table")\
             .addFloat("RT tolerance (sec):", default=10, min=0.0, help=",maximal observed deviation of "\
                       "retention times between isotopic peaks within a sample ")\
             .addFloat("mass tolereance (MMU):",default=5.0, min=0.0, max=50,
                        help="observed mass shift between measured and theoretical values")\
             .show()
              #convert mzTol to milli mass units
        mzTol=mzTol*emzed.MMU
        return rtTol, mzTol


def _setColumnOrder(table, colnames, all_pstfxs, isotopes_applied):

    colnames_order=["id", "name", "mf", "source", "total_area_mi", "z"]
    for isotope in isotopes_applied:
        colnames_order.append("isotope_fraction"+isotope)

    def sortkey_for_isotope_postfix(pf):
        # eg C13x2N15x1 -> (2, 1)
        numbers = re.findall("x(\d+)", pf)
        # map below is the same as: numbers = [int(n) for n in numbers]
        return tuple(map(int, numbers))

    all_pstfxs = sorted(all_pstfxs, key=sortkey_for_isotope_postfix)

    extract_names=[]
    # to get order
    for postfix in all_pstfxs:
        for name in colnames:
            extract_names.append(name+postfix)
    colnames_order.extend(extract_names)
    return table.extractColumns(*colnames_order)


def _isotopeOverlay(compound_table, pstfx="_1000"):
    """
    """
    supported_pstfx=compound_table.supportedPostfixes(["isotope", "num_isotopes"])
    extracted_columns=["rtmin", "rtmax", "mz", "mzmin", "mzmax", "method",
                       "area", "rmse", "mi_fraction", "peakmap", "params",
                       "source", "adduct"]
    _multipleIsotopesSplitter(compound_table)
    for pf in supported_pstfx:
       extracted_columns.extend(["isotope"+pf, "num_isotopes"+pf])

    isotopes=compound_table.splitBy("_split")
    assert len(isotopes)>=1, "not enough elements in list"
    t1=isotopes[0]
    #rename columns
    if len(isotopes)>1:
        for name in extracted_columns:
            col_0=name+pstfx
            t1.renameColumns(**{name:col_0})
        t1.addColumn("source", t1.getColumn("source"+pstfx), insertBefore="mf")
        t2=isotopes[1].extractColumns(*extracted_columns)
        tt=t1.leftJoin(t2, (t1.getColumn("source"+pstfx)==t2.source)\
            &(t1.getColumn("adduct"+pstfx)==t2.adduct))
        for i in range(2, len(isotopes)):
              t2=isotopes[i].extractColumns(*extracted_columns)
              tt=tt.leftJoin(t2, (tt.getColumn("source"+pstfx)==t2.source)
                  &(tt.getColumn("adduct"+pstfx)==t2.adduct))
    else:
        tt=t1

    _setPstfxToMi(tt, extracted_columns)

    #drop columnn source
    postfixes=tt.supportedPostfixes(["source"])
    for postfix in postfixes:
            if postfix!="":
                tt.dropColumns("source"+postfix, "adduct"+postfix)
    tt.dropColumns("_split")
    return tt

#


def _uniformColumnFormatsAndMergeTables(tables):
    """ Sets all columns to format string and type_ str prior to merge
        allows merging of tables with same column names but different formats
    """
    uniform_tables=[]
    for table in tables:
        for name in table.getColNames():
            table.set(table.colFormats, name, "%s")
            table.replaceColumn(name, table.getColumn(name), type_=str)
        uniform_tables.append(table)
    return emzed.utils.mergeTables(uniform_tables)




####################################################################
# saving
#####################################################################

def _cleanUpCsvTable(table,isotopes_applied):
    """ remove unneaded columns
    """
    # peakmap and params not neaded in csv format
    remove=["peakmap","params"]
    # the name of the isotope is now part of the colname

    rm_isotopes=["isotope"+isotope for isotope in isotopes_applied]

    check_for_empty=[ "mz", "method", "area", "rmse", "mi_fraction"]
    num_isotopes=["num_isotopes"+isotope for isotope in isotopes_applied]
    check_for_empty.extend(num_isotopes)
    supportedPostfixes=table.supportedPostfixes(remove)
    table.addColumn("rtmin_sec", table.getColumn("rtmin"+supportedPostfixes[0]),
                                                 insertBefore="total_area_mi")
    table.addColumn("rtmax_sec", table.getColumn("rtmax"+supportedPostfixes[0]),
                                                insertBefore="total_area_mi")
    for pstfx in supportedPostfixes:
        table.dropColumns("peakmap"+pstfx,"params"+pstfx, "rtmin"+pstfx,
                               "rtmax"+pstfx, "mzmin"+pstfx,  "mzmax"+pstfx)
        for name in rm_isotopes:
            table.dropColumns(name+pstfx)
    # remove columns containing only None
        for name in check_for_empty:
            if len(set(table.getColumn(name+pstfx).values))==1:
                if table.getColumn(name+pstfx).uniqueValue()=="-":
                    table.dropColumns(name+pstfx)


def _getAllPostfixesFromResultTable(table):
    """ calculates all Isotope"""
    compounds=table.splitBy("id")
    all_postfixes=[]
    for compound in compounds:
        overlayed=_isotopeOverlay(compound)
        postfixes=overlayed.supportedPostfixes(["area","rmse"])
        all_postfixes.extend(postfixes)

    return set(all_postfixes)


def _buildCsvResultTable(result_table):

    """ Transposes mass isotopomers of all compouds into a single table where
        each compound has the same number of columns. Missing mass isotopomers
        are filled with Nones.
    """
    # determin maximal number of isotopes to get total no of columns
#    colnames=["rtmin", "rtmax", "mz", "mzmin", "mzmax",
#              "method", "area", "rmse", "mi_fraction",  "peakmap",
#              "params", "source"]
    colnames=["rtmin", "rtmax", "mz", "mzmin", "mzmax",
              "method", "area", "rmse", "mi_fraction",  "peakmap",
              "params"]
    iso_ps=result_table.supportedPostfixes(["isotope","num_isotopes"])
    isotopes_applied=[]
    for ps in iso_ps:
         iso=result_table.getColumn("isotope"+ps).uniqueValue()
         isotopes_applied.append(iso)
         colnames.extend(["isotope"+iso, "num_isotopes"+iso])
    all_pstfxs=_getAllPostfixesFromResultTable(result_table)
    # get sorted columns
#    all_pstfxs=[pstfx for pstfx in all_pstfxs].sort()
    compounds=result_table.splitBy("id")
    result_by_compounds=[]
    for compound_in_samples in compounds:
        # overlay isotopes by joining
        compound_in_samples=_isotopeOverlay(compound_in_samples)
         # since column source is only required to speed up overlay:
        # add additional columns do obtain the same number of columns for
        # all compounds:
        given_pstfxs=compound_in_samples.findPostfixes()
        missing_pstfxs=set(all_pstfxs).difference(given_pstfxs)
        for pstfx in missing_pstfxs:
            for name in colnames:
                new_name=name+pstfx
                compound_in_samples.addColumn(new_name, "-")

        compound_in_samples=_setColumnOrder(compound_in_samples, colnames,
                                            all_pstfxs, isotopes_applied)
        result_by_compounds.append(compound_in_samples)

    result_csv=_uniformColumnFormatsAndMergeTables(result_by_compounds)
    _cleanUpCsvTable(result_csv, isotopes_applied)
    return result_csv


def _saveResults(result, filename, path):
     """
     """
     default_name=os.path.split(filename)[-1]
     saving, _fileName=emzed.gui.DialogBuilder("Save results")\
        .addMultipleChoice("saving results",["no","yes", "overwrite"],
                           default=[1,2])\
        .addString("file name",default=default_name)\
        .show()
     result_csv=_buildCsvResultTable(result)
     if not _fileName.endswith(".table"):
         _fileName=_fileName+".table"
     result.title="isotope analysis result of "+ _fileName.split(".")[0]
     fileName=os.path.join(path, _fileName)
     print fileName
     print saving
     if 0 in saving:
        emzed.gui.showInformation("analysis results are lost")
        return
     if 2 in saving:
          result.store(fileName, forceOverwrite=True)
          csvName=fileName.split(".")[0]+".csv"
          if os.path.exists(csvName):
              os.remove(csvName)
          emzed.io.storeCSV(result_csv, path=csvName )

     if 2 not in saving:
       if os.path.exists(fileName):
           fileName=fileName.split(".")[0] + basicOp.timeLabel() + ".table"
           result.store(fileName)
           csvName=fileName.split(".")[0]  + ".csv"
           emzed.io.storeCSV(result_csv, path=csvName )
       else:
            result.store(fileName)
            csvName=fileName.split(".")[0]+".csv"
            emzed.io.storeCSV(result_csv, path=csvName )


def _saveModifiedParameterTable(sTab, path, filename):
     assert filename.count(".")==1, "YOU ARE TOO STUPID TO CREATE "\
                                         "A CORRECT FILENAME!!"
     default_name=os.path.basename(filename)
     saving, fileName=emzed.gui.DialogBuilder("Save Modified Table")\
        .addMultipleChoice("saving modifications",["no","yes", "overwrite"],
                           default=[1,2])\
        .addString("file name",default=default_name)\
        .show()
     fileName=fileName.encode("latin-1")

     if not fileName.endswith(".table"):
         fileName=fileName + ".table"
     add=fileName.split(".")[0]
     sTab.title="istope_anal parameter table "+ add

     fileName=os.path.join(path, fileName)
     if 0 in saving:
        emzed.gui.showInformation("modifications of table are lost")
        return
     if 2 in saving:
          emzed.io.storeTable(sTab, fileName, forceOverwrite=True)
          csvName=fileName.split(".")[0]+".csv"
          if os.path.exists(csvName):
             os.remove(csvName)
          emzed.io.storeCSV(sTab, csvName )
     if 2 not in saving  and 1 in saving:
       if os.path.exists(fileName):
           emzed.gui.showWarning("The file name already exists. Please modify name"\
           "or choose the <OVERWRITE> option" )
           _saveModifiedParameterTable(sTab, path, filename)
       else:
          emzed.io.storeTable(sTab, fileName)
          csvName=filename.split(".")[0]+".csv"
          emzed.io.storeCSV(sTab, csvName )



def _saveParameterTableFix(sTab, param_path, param_filename):
    assert param_filename.count(".")==1, "YOU ARE TOO STUPID TO CREATE "\
                                         "A CORRECT FILENAME!!"
    save,overwrite=emzed.gui.DialogBuilder("Save finished parameter table")\
    .addBool("save parameter table", default=True, help="isotopes and adducts"\
            "are no longer editable. To change those values reload original table")\
    .addBool("overwrite", default=True)\
    .show()
    print param_filename
    if save:
        file_name=os.path.basename(param_filename)
        if not file_name.endswith(".table"):
            file_name=file_name + ".table"
        name, ending=file_name.split(".")
        if name.endswith("_fixed"):
            name=name+ending
        else:
            name=name+"_fixed."+ending
        sTab.title="isotope parameter table "+ name
        target=os.path.join(param_path, name)
        if os.path.exists(target):
            if overwrite:
                emzed.io.storeTable(sTab, target, forceOverwrite=True)
                csvName=target.split(".")[0]+".csv"
                if os.path.exists(csvName):
                    os.remove(csvName)
                emzed.io.storeCSV(sTab, csvName )
            else:
                target=basicOp.timeLabel()+target
                emzed.io.storeTable(sTab, target)
                csvName=target.split(".")[0]+".csv"
                emzed.io.storeCSV(sTab, csvName )

        else:
            emzed.io.storeTable(sTab, target)
            csvName=target.split(".")[0]+".csv"
            emzed.io.storeCSV(sTab, csvName )


      
     
################################################################
# MAIN FUNCTIONS
################################################################

def determineMid(sample_peaks_list):
    """input: list of tables
    """
    sample_list=[]
    for sample_peaks in sample_peaks_list:
        supported_pstfxs=sample_peaks.supportedPostfixes(["isotope", "num_isotopes"])
        colnames=["id", "area"]

        for postfix in supported_pstfxs:
            colnames.extend(["isotope"+postfix,"num_isotopes"+postfix])

        for name in colnames:
            assert sample_peaks.hasColumn(name), "column %s missing !" %name
        compounds=sample_peaks.splitBy("id")
        mid_list=[]

        for  compound in compounds:
            # to hande no integration
            compound.replaceColumn("area", compound.area.ifNotNoneElse(0.0))
            mids=compound.splitBy("adduct")
            for mid in mids:
                for pstfx in supported_pstfxs:

                    mid.updateColumn("mi_fraction", mid.area / \
                                        (mid.area.sum+1e-10), format_="%.2f")
                    # 1 e-10 added since sum area might be zero
                    mid.updateColumn("_temp"+pstfx,
                                    mid.getColumn("mi_fraction")*
                                    mid.getColumn("num_isotopes"+pstfx), format_="%.2f")

                    if mid.hasColumn("isotope_fraction"+pstfx):
                        mid.dropColumns("isotope_fraction"+pstfx)
                    mid.addColumn("isotope_fraction"+pstfx,
                                   mid.getColumn("_temp"+pstfx).sum()/\
                                   (mid.getColumn("num_isotopes"+pstfx).max()+1.0e-10),
                                   insertBefore="isotope"+pstfx)
                    mid.dropColumns("_temp"+pstfx)
                if mid.hasColumn("total_area_mi"):
                        mid.dropColumns("total_area_mi")
                mid.addColumn("total_area_mi",mid.area.sum(),
                                   format_="%.2e", insertBefore="isotope_fraction"+pstfx)

                mid_list.append(mid)
        for mid in mid_list:
            mid.setColType('total_area_mi', float)
                                
        sample_list.append(emzed.utils.mergeTables(mid_list))

    return sample_list


def modifyResultTable(result_table, files, comp):
    """
    """
    filenames, compoundnames=_getFileAndCompoundNames(result_table)
    remaining=None
    subset=result_table.copy()
    if files>0:
        print filenames[files]
        subset=subset.filter(subset.source==(filenames[files]))
        remaining=result_table.filter(~(result_table.source==(filenames[files])))
    if comp>0:
         if remaining:
             add_nonchanged=subset.filter(subset.name!=compoundnames[comp])
             remaining=emzed.utils.mergeTables([remaining, add_nonchanged])
             subset=subset.filter(subset.name==compoundnames[comp])
         else:
             remaining=subset.filter(subset.name!=compoundnames[comp])
             subset=subset.filter(subset.name==compoundnames[comp])
    emzed.gui.showInformation("Please modify peaks by reintegration")
    def _reArange(tables):
        table=emzed.utils.mergeTables(tables)
        return table.splitBy("source")
    if remaining:
        results_by_compound=subset.splitBy("id")
        results_by_compound=setUniqeColValueToTitle(results_by_compound, "name")
        emzed.gui.inspect(results_by_compound)
        results_by_compound.append(remaining)
        results_by_file=_reArange(results_by_compound)
        return emzed.utils.mergeTables(determineMid(results_by_file))
    else:
        results_by_compound=result_table.splitBy("id")
        results_by_compound=setUniqeColValueToTitle(results_by_compound, "name")
        emzed.gui.inspect(results_by_compound)
        results_by_file=_reArange(results_by_compound)
        return emzed.utils.mergeTables(determineMid(results_by_file))


def _reintegrateResultsCompoundwise(result, compound, samples, rtmin, rtmax):
    """
    """
    assert len(result)>0, ("Result table is empty!!")
    int_subset=result.filter((result.name==compound) & \
                        (result.source.isIn(samples)))
    remaining=result.filter(~((result.name==compound) & \
                        (result.source.isIn(samples))))
    #set rt window:
    if int_subset:
        int_subset.replaceColumn("rtmin", rtmin, format_="'%.2fm' %(o/60.0)")
        int_subset.replaceColumn("rtmax", rtmax, format_="'%.2fm' %(o/60.0)")
        int_subset=emzed.utils.integrate(int_subset, "emg_exact")
        #update changes due to integration
        int_subset=determineMid(int_subset.splitBy("source"))
        for t in int_subset:
            t.title=t.source.uniqueValue()
        emzed.gui.inspect(int_subset)
        int_subset=emzed.utils.mergeTables(int_subset)
        if remaining:
            return emzed.utils.mergeTables([int_subset, remaining])
        else:
            return int_subset
    else:
        return remaining


def parameterTableModifier(sTab, param_path, param_filename,
                            mzTol, features):
    """
    """
    result_table=determineIsotopeLabeling(sTab, features, mzTol,
                                           "no_integration")
    filenames, compoundnames=_getFileAndCompoundNames(result_table)
    comp=emzed.gui.DialogBuilder("Modify Integration")\
    .addChoice("select compound", compoundnames, default=0)\
    .show()
    emzed.gui.showInformation("to adapt rtmin and rtmax select 1"\
                        "peak and integrate it with std algorithm \n"\
                        "If you integrate more than 1 peak the most intensive"\
                        " one will be used to define rtmin and rtmax")

    result_table=modifyResultTable(result_table, 0, comp)
    compounds=result_table.splitBy("id")
    for compound in compounds:
        compound.title=compound.name.uniqueValue()
    emzed.gui.inspect(compounds)
    modified_rt_windows=[]
    for compound in compounds:
        # choose integrated peak with maximum area
        compound.title=compound.name.uniqueValue()
        if compound.area.max()>=0:
            replace=compound.filter(compound.area==compound.area.max())
        else:

            compound.addColumn("_temp", range(len(compound)))
            replace=compound.filter(compound._temp==0)
            replace.dropColumns("_temp")
        modified_rt_windows.append(replace)
    adapt_rt=emzed.utils.mergeTables(modified_rt_windows)
    adapt_rt=adapt_rt.extractColumns("id","name", "rtmin", "rtmax")
    adapt_rt= sTab.join(adapt_rt, sTab.id==adapt_rt.id)
    postfixes=adapt_rt.supportedPostfixes(["rtmin"])
    rt_pstfx=[pstfx for pstfx in postfixes if pstfx][0]
    adapt_rt.replaceColumn("rtmin", adapt_rt.getColumn("rtmin"+rt_pstfx),
                                                           type_=float)
    adapt_rt.replaceColumn("rtmax", adapt_rt.getColumn("rtmax"+rt_pstfx),
                                                           type_=float)
    sTab=adapt_rt.extractColumns(*sTab.getColNames())
    sTab=sTab.uniqueRows()

    return sTab


def batchLabel(sTab, samples, mzTol, rtTol, select):
    choice=select
    sample_peaks_list=[]
    for sample in samples:
#                sTab_modif_var=sTab, mzTol, adducts, sample

                result =determineIsotopeLabeling(sTab, sample, mzTol,
                                                 "emg_exact")
                if result:
                    if select !=0:
                        result=result.splitBy("id")
                        emzed.gui.inspect(result)
                        result=emzed.utils.mergeTables(result)
                        choice=emzed.gui.DialogBuilder("Choose mode")\
                        .addChoice("MODE",["continue", "next",
                                "finish"], default=1, help="continue: all "\
                                "samples are processed without inspection \n"\
                                "next: analyzing and inspecting next sample\n"\
                                "finish: analysis is stopped and analyzed samples"\
                                "will be saved")\
                        .show()
                        select=choice
                    if choice==2:
                        sample_peaks_list.append(result)
                        return determineMid(sample_peaks_list)
                    if result is not None:
                          sample_peaks_list.append(result)
    # Add mass isotopomer distribution values to table

    assert len(sample_peaks_list), "no matches found"
    return determineMid(sample_peaks_list)




def determineIsotopeLabeling(parameters, sample, mzTol, int_mode):
    """
    """
    # build labeling layout table
    #parameters=isotopeLabelingLayout(parameters)
    # enlarge table for adducts
    #parameters=basicOp.massSolutionSpace(parameters,adducts)

    if isinstance(sample, Table):

        parameters.updateColumn("source", sample.source.uniqueValue(),
                           format_="%s", insertBefore="name")
        sample=sample.peakmap.uniqueValue()
    else:
        parameters.updateColumn("source", sample.meta["source"],
                           format_="%s", insertBefore="name")
    basicOp.defineMzPeaks(parameters, sample, mzTol)
    peaks=basicOp.extractPeakParametersByIntegration(parameters, int_mode)
    # calculate
    return peaks



################################################################
#
#     GUI
#
################################################################
class stableIsotopeLabelingWorkflow(object):

    def __init__(self):
        self.samples = None
        self.sTab= None
        self.param_filename=None
        self.mzaligned_feature_tables= None
        self.labeling_data=None
        self.directories=None
        self.project_folder=None
        self.default=r"Z:"

    def _restart(self,data):
        self.samples = None
        self.sTab= None
        self.param_filename=None
        self.mzaligned_feature_tables= None
        self.labeling_data=None
        self.directories=None
        print "VALUES RESETED"




    def endDialog(self, data):
        print "END"



    def _getStructure(self, data):
        print self.project_folder
        structure=basic.checkAndGetProjectStructure(self.project_folder)
        self.mz_ranges, _, self.folders, self.label=structure

    def _getDirectories(self, data):
        # mstartgetproject
        #   [0] 'PEAKMAPS'
        #   [1] 'MZ_ALIGNED_PEAKMAPS'
        #   [2] "RT-MZ_ALIGNED_PEAKMAPS"
        #   [3] 'TOOLBOX'
        #   [4] "RESULTS"
        # msproject
        #  [0] 'RAW_FEATURES',
        #  [1] 'MZ_ALIGNED_FEATURES',
        #  [2] 'RT-MZ_ALIGNED_FEATURES',
        #  [3] 'TOOLBOX',
        #  [4] 'RESULTS'
        #
        self._getStructure(data)

        if not self.mz_ranges:
            ranges=" "

        else:
            ranges=self.mz_ranges
            sub=emzed.gui.DialogBuilder("MASS RANGE")\
            .addChoice("Select mass range", ranges)\
            .show()

        if ranges==" ":
            self.directories=[os.path.join(self.project_folder,d) \
                                for d in self.folders]
        else:
            sub=ranges[sub]

            self.directories=[os.path.join(self.project_folder,sub,d) \
                                for d in self.folders]
        result_path=os.path.join(self.directories[-1],"LabelingAnalysisResults")
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        self.directories[-1]=result_path

    def _dataManager(self, data):
        self.project_folder=data.choose_project_folder
        self._getDirectories(data)
        self._checkIfDataLoaded(data)
        self.sTab, save=buildPara.buildParameterTable_MIT(self.sTab,
                                                          self.samples)
        if save:

            _saveParameterTableFix(self.sTab, self.directories[3],
                                              self.param_filename)



    def _checkIfDataLoaded(self,data):
         if self.samples == None \
            or self.sTab== None:
                self.loadData(data)



    def loadData(self,data):
       
        if self.label==".mstargetproject":

           dlg = emzed.gui.DialogBuilder("Load Aligned Samples"\
                                        " and Labeling Parameter Table")\
           .addFilesOpen("Open Sample Files", default=[], basedir=self.directories[2],
                                                   formats="mzXML")\
           .addFileOpen("Open Labeling Parameter Table",
                      basedir=self.directories[3], formats="table")
           
           tabL, self.param_filename = dlg.show()
           self.samples=[emzed.io.loadPeakMap(name) for name in tabL]

        if self.label==".msproject":
           tabL, self.param_filename=emzed.gui.DialogBuilder("Load Aligned Samples"\
                                        " and Labeling Parameter Table")\
           .addFilesOpen("Open Sample Files", default=[], basedir=self.directories[2],
                                                      formats="table")\
           .addFileOpen("Open Labeling Parameter Table",
                      basedir=self.directories[3], formats="table")\
           .show()
           self.samples=[emzed.io.loadTable(name) for name in tabL]

        self.sTab=emzed.io.loadTable(self.param_filename)
        assert self.sTab.hasColumn("name"), "Column 'name' is missing! in "\
            "parameter table %s" %self.param_filename
        
        self.sTab.replaceColumn("name", self.sTab.name.apply(str))
        self.sTab.replaceColumn("rtmin", self.sTab.rtmin.apply(float))
        self.sTab.replaceColumn("rtmax", self.sTab.rtmax.apply(float))
        
        emzed.gui.showInformation("loaded %d sample tables, " \
                            "loaded labeling parameter table %s"
                             % (len(self.samples),self.sTab.title))

    def _loadResultTable(self, data):
        self._getDirectories(data)
        if not self.labeling_data:
            filename=emzed.gui.DialogBuilder("LOAD LABELING DATA RESULT TABLE")\
            .addFileOpen("Open Labeling Data Table",
                         basedir=self.directories[4], formats="table")\
            .show()
            self.labeling_data=emzed.io.loadTable(filename)
            



    ##########################################
    # Modify table with peak paramaters
    #########################################

    def modParameter(self,data):
        if not self.project_folder:
            self.project_folder=data.choose_project_folder
        self._getDirectories(data)
        emzed.gui.DialogBuilder("Edit parameter table")\
        .addButton("adapt rt windows", self._adaptRtWindows)\
        .addButton("build or modify table from csv file", self._addRemoveCompounds)\
        .show()



    def _addRemoveCompounds(self, data):
        """ Opens csv file in excel you can than add or remove parameters
        """

        csv_file=emzed.gui.DialogBuilder("Choose Parameter Table in format csv")\
        .addFileOpen("Choose table with labeling parameters:",
                     basedir=self.directories[3], formats="csv")\
        .show()
        emzed.utils.startfile(csv_file)
        emzed.gui.showInformation("Click ok after saving and closing Excel")
        self.sTab=emzed.io.loadCSV(csv_file)
        basicOp.timeFormats(self.sTab, ["rtmin", "rtmax"])
        emzed.gui.inspect(self.sTab)

        self.param_filename=csv_file.split(".")[0]+".table"
        _saveModifiedParameterTable(self.sTab, self.directories[3], self.param_filename)

    def _adaptRtWindows(self, data):

        if  not self.sTab:
           self.param_filename=emzed.gui.DialogBuilder("Choose Parameter Table")\
           .addFileOpen("Choose table:", basedir=self.directories[3],
                        formats="table")\
           .show()
           self.sTab=emzed.io.loadTable(self.param_filename)

        # load sample to addapt rtwindows
        if self.label==".msproject":
            sample, mzTol = emzed.gui.DialogBuilder("Sample to adapt rtmin, rtmax")\
            .addFileOpen("Choose sample to adapt rt window:",
                         basedir=self.directories[2], formats="table")\
            .addInt("mass tolerance (MMU)", default=5)\
            .show()
            features=emzed.io.loadTable(sample)
        if self.label==".mstargetproject":
            sample, mzTol = emzed.gui.DialogBuilder("Sample to adapt rtmin, rtmax")\
            .addFileOpen("Choose sample to adapt rt window:",
                         basedir=self.directories[2], formats="mzXML")\
            .addInt("mass tolerance (MMU)", default=5)\
            .show()
            features=emzed.io.loadPeakMap(sample)
        self.sTab,_ =buildPara.buildParameterTable_MIT(self.sTab, [features])
        #[features] since function
        # takes list of tables
        mzTol=mzTol*emzed.MMU
        self.sTab=parameterTableModifier(self.sTab, self.directories[3],
                                         self.param_filename, mzTol,  features)
        _saveParameterTableFix(self.sTab, self.directories[3],
                               self.param_filename)
#        _saveModifiedParameterTable(self.sTab, self.param_path, self.param_filename)
        return self.sTab
############################################################################
# Run Data Analysis
############################################################################
    def _stepRun(self, data):

        self._dataManager(data)

        # create folder for quantification results
        adducts=basicOp.adductsDialog(self.samples)
        rtTol,mzTol=_rtMzDialog()
        #mode of analysis
        select=1
        labeling_data=batchLabel(self.sTab, self.samples, mzTol, rtTol,
                                        adducts, select)
        self.labeling_data=emzed.utils.mergeTables(labeling_data)
        self.modifyAndStore(data)

    def _batchRun(self,data):

        self._dataManager(data)
#        adducts=basicOp.adductsDialog(self.samples)
        rtTol,mzTol=_rtMzDialog()
        #mode of analysis
        select=0
        labeling_data=batchLabel(self.sTab, self.samples, mzTol,
                                        rtTol, select)

        self.labeling_data=emzed.utils.mergeTables(labeling_data)
        self.modifyAndStore(data)

########################################################
# Inspect and Store Results

    def modifyAndStore(self,data):
        """
        """
        self.project_folder=data.choose_project_folder
        if not self.labeling_data:
            self._loadResultTable(data)

        target=os.path.split(self.project_folder)[-1]+\
                "_labeling_analysis_results.table"
        filename=emzed.gui.DialogBuilder("INSPECT, MODIFY")\
        .addString("save file as", default=target)\
        .addButton("modify results", self._modify)\
        .addButton("inspect results", self._inspect)\
        .addButton("inspect filtered results", self._filteredInspect)\
        .show()
        # add current time to filename to avoid overwriting results
        filename=filename[0] # filename is n-tuple
        if self.labeling_data:
            _saveResults(self.labeling_data, filename, self.directories[4])


    def _modify(self, data):
        """
        """

        filenames, compoundnames=_getFileAndCompoundNames(self.labeling_data)
        no, files, comp=emzed.gui.DialogBuilder("Modify Integration")\
        .addButton("modify critical peaks", self._showCritical,
                   help="under construction")\
        .addButton("set compound's RT window and reintegrate peaks"\
                    , self._setCompoundRtWindowsAndReintegrate, help= \
                    "Rt windows for selected compound is set manually and all"\
                    " compound peaks are reintegrated for selected samples")\
        .addButton("modify peaks manually", self._modifyPeakWise,
                   help="single peaks can be modified with options"\
                   " 'compound wise' and 'sample wise'")\
        .show()


    def _modifyPeakWise(self, data):
        """
        """
        filenames, compoundnames=_getFileAndCompoundNames(self.labeling_data)
        files, comp=emzed.gui.DialogBuilder("Modify Integration")\
        .addChoice("select file", filenames,default=0)\
        .addChoice("select compound", compoundnames, default=0)\
        .show()
        self.labeling_data=modifyResultTable(self.labeling_data, files, comp)

    def _setCompoundRtWindowsAndReintegrate(self, data):
        """
        """
        samples, compoundnames = _getFileAndCompoundNames(self.labeling_data)
        # remave option "all"
        compoundnames = compoundnames[1:]
        samples=samples[1:]
        selected_compound, selected_samples, rtmin, rtmax = \
             emzed.gui.DialogBuilder("Set Rt window and reintegrate compound peaks")\
        .addChoice("select compound", compoundnames, default=0)\
        .addMultipleChoice("select samples", samples, vertical=3, default=[0])\
        .addFloat("rtmin ",default=10.0, unit="minutes")\
        .addFloat("rtmax ",default=20.0, unit="minutes")\
        .show()
        # convert rtmin, rtmax to seconds
        rtmin=rtmin*60.0
        rtmax=rtmax*60.0
        compound=compoundnames[selected_compound]
        samples=[samples[i] for i in selected_samples]
        self.labeling_data=_reintegrateResultsCompoundwise(self.labeling_data,
                            compound, samples, rtmin, rtmax)



    def _inspect(self,data):

        compounds=self.labeling_data.splitBy("id")
        overlayed_compound_list=[]
        for compound_table in compounds:
            compound_table=_isotopeOverlay(compound_table)
            compound_table.title=str(compound_table.name.uniqueValue())
            overlayed_compound_list.append(compound_table)
        emzed.gui.inspect(overlayed_compound_list)

    def _filteredInspect(self, data):

        min_fraction=emzed.gui.DialogBuilder("Filter results for reduced No of overlays")\
        .addFloat("min fraction of Mi", default=0.01,
                  help="minimal fraction of isotopomer in MID")\
        .show()
        reduced_results=_resultFilter(self.labeling_data, min_fraction)
        compounds=reduced_results.splitBy("id")
        overlayed_compound_list=[]

        for compound_table in compounds:
            if compound_table:
                compound_table=_isotopeOverlay(compound_table)
                compound_table.title=str(compound_table.name.uniqueValue())
                overlayed_compound_list.append(compound_table)
        emzed.gui.inspect(overlayed_compound_list)

    def _showCritical(self, data):
        emzed.gui.showInformation("UNDER CONSTRUCTION")
        pass


    def run(self):
        emzed.gui.DialogBuilder("Stable Isotope Labeling Analyzer Tool")\
        .addDirectory("choose project folder", default=self.default,
                      help="Folder containing existing project structure\n")\
        .addButton("Modify Labeling Parameter Table", self.modParameter,
                   help=("adaptation based on choosen sample"))\
        .addButton("Stepwise Analysis", self._stepRun)\
        .addButton("Batch Run", self._batchRun)\
        .addButton("Modify and Store results", self.modifyAndStore)\
        .addButton("Restart analysis with new dataset", self._restart)\
        .show()

        return

#workflow = stableIsotopeLabelingWorkflow()
#path = workflow.run()