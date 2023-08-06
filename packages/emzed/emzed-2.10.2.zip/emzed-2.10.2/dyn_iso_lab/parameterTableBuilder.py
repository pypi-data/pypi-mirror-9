# -*- coding: utf-8 -*-
"""
Created on Wed Mar 06 15:23:25 2013

@author: pkiefer
"""
import emzed
import emzed.mass as mass
import re
import emzed.adducts as adducts
import basicEmzedOperations as basicOp
from emzed.core.data_types import PeakMap, Table


def _isotopeLabelingLayout(parameters):
    """ Builds masses from stable isotope ranges
        required columns: name mf rtmin rtmax isotope isotopemin isotopemax
    """
    required=["id","name", "mf", "rtmin", "rtmax"]
    required1=[ "isotope", "isotopemin",
              "isotopemax"]
    basicOp.checkColnames(required, parameters)
    basicOp.checkColnames(required1, parameters)
    _checkMf(parameters)
    compounds=parameters.splitBy("id")
    compound_list=[]
    for compound in compounds:
        # get isotopes
        isotope_columns=["isotope", "isotopemin", "isotopemax"]
        supportedPostfixes=compound.supportedPostfixes(isotope_columns)
        isotope_types=[]
        isotope_names=[]

        for i,postfix in enumerate(supportedPostfixes):
            min_iso=compound.getColumn(isotope_columns[1]+postfix).uniqueValue()
            max_iso=compound.getColumn(isotope_columns[2]+postfix).uniqueValue()+1
            iso=isotope_columns[0]+postfix
            isotope_names.append(iso)
#            ident=compound.getColumn(iso).uniqueValue()
            compound.updateColumn("_delta_isotope",
                                 compound.getColumn(iso).apply(basicOp._deltaIsotope))
            table=compound.extractColumns("id", "name", "mf", "rtmin",
                                                  "rtmax","_delta_isotope",
                                                "isotope"+postfix,)
            if postfix:
                table.renameColumns(**{"isotope"+postfix:"isotope"})
            isotope_tables=[]
            for num in range(min_iso, max_iso):
                   new_tab=table.copy()
                   new_tab.updateColumn("mass_shift",
                                        num * new_tab._delta_isotope, format_="%.5f")
                   new_tab.updateColumn("num_isotopes", num, format_="%d")
                   new_tab.dropColumns("_delta_isotope")
                   isotope_tables.append(new_tab)
            isotope_types.append(emzed.utils.mergeTables(isotope_tables))
        # removes redundant isotopes if same isotope is several times in
        # parameter table
        isotope_types=_remove_redundant_isotopes(isotope_types)
        for i in range(len(isotope_types)):
                if i==0:
                    tt=isotope_types[i]
                else:
                    table=isotope_types[i]
                    tt=tt.join(table,True)
        postfixes=tt.supportedPostfixes(["mass_shift"])
        tt.updateColumn("mass", tt.mf.apply(mass.of),
                             format_="%.5f")
        for postfix in postfixes:
            col="mass_shift"+postfix
            tt.replaceColumn("mass", tt.mass+ tt.getColumn(col))
            tt.dropColumns(col)
        # remove redundant columns in case more than 1 isotope is present
        postfx=tt.supportedPostfixes(required)
        for rem in postfx:
            if rem !="":
                for colname in required:
                    col=colname+rem
                    tt.dropColumns(col)

        compound_list.append(tt)
        s_tab=emzed.utils.mergeTables(compound_list)
        postfixes=s_tab.supportedPostfixes(["num_isotopes"])
        for ps in postfixes:
            new_ps=s_tab.getColumn("isotope"+ps).uniqueValue()
            s_tab.renameColumns(**{"isotope"+ps:"isotope"+new_ps})
            s_tab.renameColumns(**{"num_isotopes"+ps:"num_isotopes"+new_ps})
    return s_tab


def _remove_redundant_isotopes(tables):
    isotope_names=[table.isotope.uniqueValue() for table in tables]
    redundant_names=set(name for name in isotope_names if isotope_names.count(name)>1)
    merge_tables=[table for table in tables \
                if table.isotope.uniqueValue() in redundant_names]
    return_tables=[table for table in tables \
                if table.isotope.uniqueValue() not in redundant_names]
    if merge_tables:
        for name in redundant_names:
            merge_list=[]
            for table in merge_tables:
                if table.isotope.uniqueValue()==name:
                    merge_list.append(table)
            if merge_list:
               merged_table=emzed.utils.mergeTables(merge_list)
               split_by_isotopes=merged_table.splitBy("num_isotopes")
               removed_double=[]
               for t in split_by_isotopes:
                   t.addColumn("_id", range(len(t)))
                   t=t.filter(t._id<1)
                   t.dropColumns("_id")
                   removed_double.append(t)

               return_tables.append(emzed.utils.mergeTables(removed_double))
    return return_tables


def _checkMf(parameters):
    
    """ checks whether the number range of selected isotopea in parameter
        table is conform with the molecular formula
    """
    import elements
    isotope_columns=["isotope", "isotopemin", "isotopemax"]
    compounds=parameters.splitBy("id")
    for compound in compounds:
         supportedPostfixes=compound.supportedPostfixes(isotope_columns)
         for postfix in supportedPostfixes:
            isotope=compound.getColumn(isotope_columns[0]+postfix).uniqueValue()
            isotopemin=compound.getColumn(isotope_columns[1]+postfix).uniqueValue()
            isotopemax=compound.getColumn(isotope_columns[2]+postfix).uniqueValue()
            mf=compound.mf.uniqueValue()
            mass_shift_min=basicOp._deltaIsotope(isotope)*isotopemin
            mass_shift_max=basicOp._deltaIsotope(isotope)*isotopemax
            element=re.split("[0-9]", isotope)[0]
            
            expr="elements."+isotope
#            x= mass.of(mf, **{element: eval(expr)}) - mass.of(mf)\
#                            -mass_shift_min
#            y= mass.of(mf, **{element: eval(expr)})\
#                            -mass.of(mf) - mass_shift_max
            assert mass.of(mf, **{element: eval(expr)}) - mass.of(mf)\
                            -mass_shift_min >=-1e-3 and \
                            mass.of(mf, **{element: eval(expr)})\
                            -mass.of(mf) - mass_shift_max >=-1e-3,\
                            "choosen range for isotope %s (%d - %d) is not"\
                            " consitent with molecular formula %s" \
                            %(isotope, isotopemin, isotopemax, mf)







def _getPolarity(items):

    is_peakmaps = all( [isinstance(t, PeakMap) for t in items])
    is_tables = all( [isinstance(t, Table) for t in items])
    print is_tables
    if not is_peakmaps and not is_tables:
        assert False, "need either peakmaps or tables as input"
    if is_tables:
        items=[t.peakmap.uniqueValue() for t in items]
    polarity=[pm.polarity for pm in items]
    assert len(set(polarity))==1, "polarity in peakmap not unique"
    return polarity[0]


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

def _checkPolarityConsistency(table, items):
    """
    """
    polarity_items=_getPolarity(items)
    is_negative=all([v<0 for v in table.mass_shift.values])
    is_positive=all([v>0 for v in table.mass_shift.values])
    if is_negative:
        polarity_table="-"

    if is_positive:
        polarity_table="+"
    if not is_positive and not is_negative:
        assert False, "polarity in calibration tables are not unique"
    if polarity_items==polarity_table:
        return True
    else:
        assert False, "adducts in calibration table are not consistent with"\
                        "those in samples"


def buildParameterTable_MIT(table, samples):
    """ Builds a parameter table for multiple isotope analysis tool. 
    """
    required=["id","name", "mf", "rtmin", "rtmax"]
    basicOp.checkColnames(required, table)
    if table.hasColumns("mzTheo", "adduct", "mass", "z"):
        required1=["isotope", "num_isotopes"]
        basicOp.checkColnames(required1, table )
        _checkPolarityConsistency(table, samples)
        return table, False

    else:
        required1=[ "isotope", "isotopemin", "isotopemax"]
        basicOp.checkColnames(required1, table)
    polarity=_getPolarity(samples)
    mode=emzed.gui.DialogBuilder("Add adduct values")\
    .addBool("individual adducts for each compound", default=True)\
    .show()

    if mode:
        compounds=table.splitBy("name")
        cal_list=[]
        for compound in compounds:
            title=emzed.gui.DialogBuilder(compound.name.uniqueValue()+\
                                    ": choose adducts ")
            compound=_isotopeLabelingLayout(compound)
            adduct=_getAdducts(polarity, title)

            cal_list.append(basicOp.massSolutionSpace(compound, adduct))
        result=emzed.utils.mergeTables(cal_list)
#        result.renameColumns(mzTheo="mz")

    else:

        if polarity=="+":
            adduct=adducts.positive.buildTableFromUserDialog()
        if polarity=="-":
            adduct=adducts.negative.buildTableFromUserDialog()
        table=_isotopeLabelingLayout(table)
        result=basicOp.massSolutionSpace(table, adduct)
#    result.info()

    return result, True

def buildParameterTable_IDMS(table, samples):
    #######################
    # BEDINGUNG !!!!
    
    required=["name", "mf", "rtmin", "rtmax"]
    additional=['abundance', 'adduct', 'mass_shift', 'mfIon', 'mzTheo', 'z']
    if table.hasColumns(*additional):
        _checkPolarityConsistency(table, samples)
        return table, False

    basicOp.checkColnames(required, table)
    polarity=_getPolarity(samples)
    mode=emzed.gui.DialogBuilder("Add adduct values")\
    .addBool("individual adducts for each compound", default=True)\
    .show()
    if mode:
       compounds=table.splitBy("name")
       cal_list=[]
       for compound in compounds:
           title=emzed.gui.DialogBuilder(compound.name.uniqueValue()+\
                                    ": choose adducts ")

           adduct=_getAdducts(polarity, title)

           cal_list.append(basicOp.massSolutionSpace(compound, adduct))
       result=emzed.utils.mergeTables(cal_list)

    else:

        if polarity=="+":
            adduct=adducts.positive.buildTableFromUserDialog()
        if polarity=="-":
            adduct=adducts.negative.buildTableFromUserDialog()

        result=basicOp.massSolutionSpace(table, adduct)

    return _enlargeTableForNaturalIsotopes(result), True

def _enlargeTableForNaturalIsotopes(table):
    """
    """
    assert table.hasColumn("mf") and table.hasColumn("adduct"),("Columns mf"\
        " and adduct_name  are mandatory")
    if table.hasColumn("_iso_calc"):
        table.dropColumns("_iso_calc")
    if table.hasColumn("_mfIon"):
        table.dropColumns("_mfIon")
    if table.hasColumn("_id"):
        table.dropColumns("_id")
    table.addColumn("_iso_calc", table.adduct +"**"+table.mf )
    table.addColumn("mfIon", table._iso_calc.apply(_buildMfIon))
    table.dropColumns("_iso_calc")
    table.addColumn("_id", range(len(table)))
    isotopes=table.splitBy("_id")
    enlarged_tables=[]
    R=60000 #Orbitrap standard resolution for acquisistion
    for entry in isotopes:
        mfIon=entry.mfIon.uniqueValue()
        #calculating m/z dependend resolutiob of mf ion
        Rres=(400/mass.of(mfIon))**0.5*R
        isotope_table=emzed.utils.isotopeDistributionTable(mfIon,R=Rres)
        entry.dropColumns("_id")
        entry=entry.join(isotope_table, True)
        # since isotope of mfIon mass is calculated
        entry.replaceColumn("mzTheo", entry.mass__0/entry.z)
        entry.dropColumns("mf__0", "mass__0")
        entry.renameColumns(abundance__0="abundance")
        enlarged_tables.append(entry)

    return emzed.utils.mergeTables(enlarged_tables)

def _buildMfIon(mf_linked):
    adduct, mf=mf_linked.split("**")
    mf_plus,mf_minus=_adductMf(adduct)
    mf_minus="-"+mf_minus
    return emzed.utils.addmf(mf,mf_plus,mf_minus)

def _adductMf(entry):

    start, end = entry.find("M")+1,entry.find("]")
    entry=entry[start:end]
    sett=["",""]

    for parts in entry.split("+"):
        res=[mod for mod in parts.split("-")]
        if len(res)==1:
            sett[0]=sett[0]+res[0]
        if len(res)>1:
           sett[0]=sett[0]+res[0]
           for add in res[1:]:
               sett[1]=sett[1]+add

    return sett