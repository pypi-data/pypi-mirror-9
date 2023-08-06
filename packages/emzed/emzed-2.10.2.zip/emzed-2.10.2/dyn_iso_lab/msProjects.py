# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 11:35:10 2011

@author: pkiefer
"""
import emzed
import os
import shutil
import glob



##############################################
# functions to create data eMZed projects
#############################################

def proposeMassRanges(file_name_list):
    """ Proposes name of mass ranges annotated in the peakmap filename. This
        is a helper function to create a eMZed data analysis project
    """
    decomp_names=[]
    for name in file_name_list:
        assert name.split("_"), +"file names are not conform"
        # remove pass
        base_name=os.path.split(name)[-1]
        base_name=base_name.split(".")[0]
        if not "blank" in base_name: # remove blanks
            fields=base_name.split("_")

            decomp_names.append((len(fields), fields))

    length=max([l[0] for l in decomp_names])

    decomp_names=[name[1] for name in decomp_names if name[0]==length]

    groups=[]
    for i in range(length):
        ele=set([part[i] for part in decomp_names])

        groups.append(ele)
    #assumptions: there are 3 mass ranges applies:
    # 1. only one mass ranges
    candidates=[entry for entry in groups if 2<=len(entry)<=3]
    if not candidates:
        candidates=[entry for entry in groups if len(entry)<=3]

    convert=[]
    if candidates:
        for name in candidates:
            merged=""
            for n in name:
                merged=merged+" "+ str(n)
            convert.append(merged)
        print convert

        ident, no_recog=emzed.gui.DialogBuilder("choose mass range identifier")\
        .addChoice("choose identifier",convert)\
        .addBool("Not listed", default=False)\
        .show()
        ident=candidates[ident]
    else:
        no_recog=True
    if no_recog:
        ident=emzed.gui.DialogBuilder("Mass range Identifyer")\
        .addString("please enter identifyers id1;id2;..")\
        .show()

        ident=ident.split(";")

    assert 0<len(ident)<=3, "too many or not enough "\
                                "mass range identifyers "
    print ident
    return ident

def _checkPath(path, directories):
    """ checks whether given path for new project is conform with
        mandatory data and older structure.
    """
    types=[".msproject", ".mstargetproject", ".msdiscoveryproject"]
    fields=path.split(os.sep)
    for type_ in types:
        while len(fields):
            sub=os.sep.join(fields)+type_
            if os.path.exists(sub):
               emzed.gui.showWarning('Chosen Folder is part of an existing project %s!!'\
                             'PLEASE CHOOSE / CREATE AN OTHER FOLDER' %sub)
               return
            fields.pop()
    #check whether other files exist which are not of type .mzXML or .raw
    folderelements=os.listdir(path)

    if any([os.path.isdir(elem) for elem in folderelements]):
        emzed.gui.showWarning("CHOSEN FOLDER CONTAINS SUBFOLDERS "\
                        'IF YOU WANT TO CREATE A NEW PROJECT:'\
                        'PLEASE CHOOSE or CREATE AN OTHER FOLDER ELSEWHERE')
        return

    return True


def _getProjectDirectories(path, type_):
    """
    """

    peakmapsDirectory="PEAKMAPS"
    mzAlignedPeakmapsDirectory = "MZ_ALIGNED_PEAKMAPS"
    if type_==".msdiscoveryproject":
        rtMzAlignedDirectory = "RT-MZ_ALIGNED_TABLES"
    if type_==".mstargetproject":
        rtMzAlignedDirectory = "RT-MZ_ALIGNED_PEAKMAPS"
    resultsDirectory="RESULTS"
    toolboxDirectory='TOOLBOX'

    directories_list=[peakmapsDirectory,
                    mzAlignedPeakmapsDirectory,rtMzAlignedDirectory,
                    resultsDirectory, toolboxDirectory]
    paths_list=[]
    for directory in directories_list:
        directory=os.path.join(path , directory)
        paths_list.append(directory)
    return paths_list

def createProject(path, type_):

    """ creates folder tree for alignment tool. The tree is made for
        targeted data analysis where known peaks are directly extracted from
        peakmaps using a parameter table e.g. idmsQuan and
        multipleIsotopesLabelingAnalysis.
    """

    assert type_ in [".mstargetproject", ".msdiscoveryproject"], "The"\
                                            " project type doesn't fit!!"
    dir_=_getProjectDirectories(path, type_)
    if _checkPath(path, dir_):
        xcal=["RAW","XCALIBUR_DATA"]
        xcal_directories=[os.path.join(path, dire_) for dire_ in xcal]

        dir_.extend(xcal_directories)
        # create folders with raw file and XCALIBOR data:

        for name in xcal_directories:
            os.mkdir(name)
        target_path=os.path.join(path,'*.zip')
        for rawfile in glob.glob(target_path):
            shutil.move(rawfile, xcal_directories[0])

        # create subproject label

        open(os.path.join(path, type_),'w').close()

        # get mass ranges and create subfolders with mass range identifyers
        target_path=os.path.join(path,'*.mzXML')
        file_names=[name for name in glob.glob(target_path)]
        mz_ranges=proposeMassRanges(file_names)
        #create subfolders
        for range_ in mz_ranges:
            os.mkdir(os.path.join(path,range_))
            directories=_getProjectDirectories(os.path.join(path, range_), type_)
            # created directories
            for name in directories:
                os.mkdir(name)
                print name

            # move mz_files into corresponding subfolders
            identifyer="*.mzXML"
            target_path=os.path.join(path, identifyer)
            _get_mzxml=glob.glob(target_path)
            
            identifyer="*"+range_ +"*"
            print identifyer
            target_path=os.path.join(path, identifyer)
            _get_range=glob.glob(target_path)
            files=set(_get_range).intersection(set(_get_mzxml))
            if not files:
                print path
                emzed.gui.showWarning("no mzXML files could be identified. Please "\
                "choose mass files for mass range %s manually" %range_)
                files=emzed.gui.askForMultipleFiles("select files for mass range"\
                " %s" %range_, startAt=path)
            print files
            for mzxml in files:
                
                # move files into corresponding folders
                shutil.move(mzxml, directories[0])
            #  check whether unidentified peakmaps remain
            identifyer="*.mzXML"
            target_path=os.path.join(path, identifyer)
            remaining=glob.glob(target_path)
        if remaining:
           target_path=os.path.join(path,"unknown_mz_range")
           os.mkdir(target_path)
           directories=_getProjectDirectories(target_path, type_)
           for name in directories:
               os.mkdir(name)
           for mzxml in remaining:
               shutil.move(mzxml, directories[0])
           emzed.gui.showInformation("for some peakmaps the mass range\n"\
           " could not be identified they were moved into folder\n"\
           " `unknown_mz_range`")
        #move all other files into XCALIBUR_DATA folder
        target_path=os.path.join(path,'*.*')
        for remaining in glob.glob(target_path):
             shutil.move(remaining, xcal_directories[-1])
    emzed.gui.showInformation("Done")
    return directories



def remove_mz_align(path):
    """ Function removes intermediate mz aligned peakmaps built during
        peakmap alignment
    """
    identifyer="*_mz_aligned.mzXML"
    target_path=os.path.join(path, identifyer)
    _get_mzxml=glob.glob(target_path)
    for mzxml in _get_mzxml:
        # move files into corresponding folders
       os.remove(mzxml)

def checkAndGetProjectStructure(path):
    """ Function identifies project structure in path and 
        returns type and folder structure of project
    """
    projects={
        ".msproject": ["RAW", "MZXML", "RAW_FEATURES",
                            "MZ_ALIGNED_FEATURES", "RT-MZ_ALIGNED_FEATURES",
                            "TOOLBOX", "RESULTS"],
        ".mstargetproject" : ["RAW", "XCALIBUR_DATA", "PEAKMAPS",
                             "MZ_ALIGNED_PEAKMAPS", "RT-MZ_ALIGNED_PEAKMAPS",
                             "TOOLBOX", "RESULTS"],
        ".msdiscoveryproject": ["RAW", "XCALIBUR_DATA", "PEAKMAPS",
                             "MZ_ALIGNED_PEAKMAPS", "RT-MZ_ALIGNED_TABLES",
                             "TOOLBOX", "RESULTS"]}


    items=os.listdir(path)
    subfolders=[s for s  in items if os.path.isdir(os.path.join(path,s))]
    labels=set([".msproject", ".mstargetproject", ".msdiscoveryproject"])
    project_types=labels.intersection(items)
    assert len(project_types)==1, "choosen poject folder is"\
                                            " not a ms project !!"
    project_type=project_types.pop()

    folders = projects[project_type]

    if project_type==".msproject":
        assert set(folders)==set(subfolders), "Project type does"\
                         " not fit with subfolders in project folder"
        return None, folders[:2], folders[2:], ".msproject"
    if not set(folders)==set(subfolders):
        in_sub=set(folders)-set(subfolders)
        ranges=list(set(subfolders)-set(folders))
        assert len(ranges)>0, "please check data structure"
        for sub in ranges:
           check=set([s for s  in in_sub\
                    if os.path.isdir(os.path.join(path,sub,s))])
           if check!=in_sub:
              not_in_check= in_sub.difference(check)
              if len(not_in_check)>0:
                  names=""
                  for name in not_in_check:
                      names=names + name + ", "
                  assert False, "Folder(s) %s are missing "\
                                "in subfolder %s" %(names, sub)
        return ranges, folders[:2],folders[2:], project_type
    assert project_type==".mstargetproject","Project label"\
                                    " does not fit with folder structure !"
    return None, folders[:2],folders[2:], ".mstargetproject"



