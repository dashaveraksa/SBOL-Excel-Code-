###Uncomment all import statements if NOT running with Jupyter Notebook
#need to install pysbol, xlrd


#from sbol import *
#import re
#import sys
#import xlrd

"""""
EXCEL IMPORT
"""""
def MakeBook(file_location):
    wb = xlrd.open_workbook(file_location)
    return wb

def ExcelImport(wb):
    try:
        ExperimentSheet = wb.sheet_by_name('Experiment DNA sample')
    except:
        print('Error: No sheet named "Experiment DNA sample" detected.')
    #sys.exit()
        return(-1,-1)
    #searching for Experiment Name header in the first column of Experiment sheet, with the experiment name directly below it
    NameSheet = wb.sheet_by_name('Experiment')
    LookingFor = 'Experiment Name'
                # possible error: need a sheet named Experiment
    for r in range(0,NameSheet.nrows):
        cell_obj = NameSheet.cell(r,0)
        if (cell_obj.value == LookingFor):
            break
        else:
            r+=1
    #if there is no Experiment Name header in the first column, user can input it--otherwise it is found in the row under the Experiment Name header
    if (r == NameSheet.nrows):
        ExperimentName = input('Experiment Name not found in file. Enter it now: ')
    else:
        r+=1
        ExperimentName = (NameSheet.cell(r,0)).value
    #error: need Experiment Name in first column of Experiment
    return(ExperimentName,ExperimentSheet)

def UnitCollectionFunc(ExperimentSheet):
    #finding unit -- watch out, there could be errors
    Unit = ''

    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if (cell_obj.value == 'Unit:' or cell_obj.value == 'Unit' or cell_obj.value == 'unit:' or cell_obj.value == 'unit'):
            Unit = (ExperimentSheet.cell(r,1)).value
        else:
            r+=1
    if Unit == '':
        print('Error: Unit not found.')
        return(-1)
    return(Unit)

    #error: need Unit and Collection header in first column of datasheet

    #creating a list of the plasmid numbers/module names
def PlasModList(ExperimentSheet):
    ModList = []
    LookingFor = 'Plasmid Number'

    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if cell_obj.value == LookingFor:
            col = 1
            while (ExperimentSheet.cell(r,col)).value != '' and (ExperimentSheet.cell(r,col)).value != 'Plasmid Description':
                ModList.append(ExperimentSheet.cell(r,col).value)
                col+=1
        else:
            r+=1
    if ModList == []:
        print('Error: No modules found. They need to be in a row with "Plasmid Number" as the header.')
        return(-1,-1)
    ModDescriptionList = ["5 ng Blank, 50 ng Blank","35 ng Blank, 20 ng LC41","45 ng Blank, 10 ng LC41","5 ng Blank, 50 ng LC20","15 ng Blank, 40 ng LC20","45 ng FlpO, 10 ng LC41"]

    #creating a list of plasmids
    PlasmidList_orig = []
    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if (cell_obj.value == LookingFor):
            r+=1
            while (r < ExperimentSheet.nrows and (ExperimentSheet.cell(r,0)).value != ''):
                PlasmidList_orig.append((ExperimentSheet.cell(r,0)).value)
                r+=1
    if PlasmidList_orig == []:
        print('Error: No plasmids found. They need to be in the first column with "Plasmid Number" as the header.')
        return(-1,-1)
    return(ModList,PlasmidList_orig)

def PlasNoRepeat(PlasmidList_orig):
    #takes away duplicates from PlasmidList_orig so that unique CD can be created
    import collections
    PlasmidList_norepeat = list(dict.fromkeys(PlasmidList_orig))
    return(PlasmidList_norepeat)


#function for finding a cell with a specific string
def DescriptionFinder(LookingFor,sheetname):
    for r in range(0,sheetname.nrows):
        for c in range(0,sheetname.ncols):
            cell_obj = sheetname.cell(r,c)
            if cell_obj.value == LookingFor:
                return (r,c)
    return(-1,-1) ###make an error message


"""""
SBOL SETTINGS
"""""

#global doc = Document()
#setHomespace('http://bu.edu/dasha')
#Config.setOption('sbol_typed_uris',False)
#Config.setOption('sbol_compliant_uris',True)


"""""
MODULE DEFINITIONS -- DNA MIXES
"""""

#this takes the module name/plasmid number and puts a '_' where the spaces are, then composes the ModuleNames into a new list
def ModListCleaner(ModList,ExperimentName):
    clean = lambda varStr: re.sub('\W|^(?=\d)','_', varStr)
    newModList = [(ExperimentName + '_codename' + clean(ModName)) for ModName in ModList]
    return(newModList)

def ModMaker(ExperimentSheet,ModList,newModList):
    ModDefDict = {}
    #this makes a dictionary with the key being the MD displayID and the value being the MD associated with that displayID, then adds appropriate description to each MD
    for val in range(0,len(newModList)):
        displayID = newModList[val]
        try:
            temp = ModuleDefinition(displayID)
            ModDefDict[displayID] = temp
            #temp.description = ModDescriptionList[val]
            #insert description by extracting it from the Excel files
            doc.addModuleDefinition(ModDefDict[displayID]) #ModDefDict[displayID] is of the type "MD"
        except:
            formatlist = [ExperimentSheet.name,ModList[val]]
            print('Error: Detecting two columns in "{}" sheet with {} as the condition header.'.format(*formatlist))
            return(-1)
#sys.exit()
    return(ModDefDict)

"""""
MODULE DEFINITIONS -- SAMPLES
"""""

def SamplesImport(ModList,newModList,ModDefDict,wb,ExperimentName):
    try:
        SampleSheet = wb.sheet_by_name('Samples')
    except:
        print('Error: No sheet named "Samples" detected.')
        #sys.exit()
        return(-1)
    #importing data from the Samples tab
    SampleList = []
    SampleDescriptions = []

    for r in range(0,SampleSheet.nrows):
        cell_obj = SampleSheet.cell(r,0)
        if (cell_obj.value == 'SAMPLE\nNUMBER' or cell_obj.value == 'SAMPLE NUMBER'):
            r+=1
            while (SampleSheet.cell(r,0)).value != '':
                SampleList.append(SampleSheet.cell(r,0).value)
                SampleDescriptions.append(SampleSheet.cell(r,1).value)
                r+=1
        else:
            r+=1
    if SampleList == []:
        print('Error: First column in "Samples" sheet must have a column name SAMPLE NUMBER')
        return(-1)

    #getting data about Experimental Conditions -- ASSUMING THERE ARE 5 POSSIBLE COLUMNS
    ConditionList1 = []
    ConditionList2 = []
    ConditionList3 = []
    ConditionList4 = []
    ConditionList5 = []

    LookingFor ='Experimental Conditions (one per column, can vary). '
    try:
        (r,c) = DescriptionFinder(LookingFor,SampleSheet)
    except:
        try:
            (r,c) = DescriptionFinder('Experimental Conditions',SampleSheet)
        except:
            print('Error: "Samples" sheet must have a column titled "Experimental Conditions" or "Experimental Conditions (one per column, can vary). ".')
            return(-1)
    r+=1
    for cond in [ConditionList1,ConditionList2,ConditionList3,ConditionList4,ConditionList5]:
        for row in range(r,r+1+len(SampleList)):
            addval = (SampleSheet.cell(row,c)).value
            cond.append(addval)
            row+=1
        c+=1

    #checking if a string is a number
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    #creating Module Defs
    SampleModDefDict = {}
    newSampleList = [(ExperimentName + '_sample_' + str(round(SampleName))) for SampleName in SampleList]
    for val in range(0,len(newSampleList)):
        displayID = newSampleList[val]
        try:
            temp = ModuleDefinition(displayID)
            SampleModDefDict[displayID] = temp
            temp.description = SampleDescriptions[val]
            doc.addModuleDefinition(SampleModDefDict[displayID])
        except:
            formatlist = [SampleSheet.name,SampleList[val]]
            print('Error: Detecting two samples in "{}" sheet numbered {}.'.format(*formatlist))
            return(-1)
        #sys.exit()
        #creating annotations with Dox symbol, time, and any other experimental conditions listed
        for cond in [ConditionList1,ConditionList2,ConditionList3,ConditionList4,ConditionList5]:
                if(cond[0] != '' and cond[0] != '-'):
                    tempURI = temp.identity + '#' + cond[0]
                    value = cond[val+1]
                    if value != '':
                        if is_number(value):
                            stringval = '%s' % float('%6g' % value)
                            #at most 6 significant figures
                            temp.setAnnotation(tempURI,stringval)
                        else:
                            stringval = value
                            temp.setAnnotation(tempURI,stringval)

    ##NEXT STEP: have the computer extract information about the condition keys (aka each explanation) so that when adding annotation it can be added as 0 ng instead of - or 100 ng instead of +
    
    #creating Modules for each of the plasmid mixes and adding them to the appropriate Sample MD
    isthereCode = 0
    for val in range(0,len(SampleList)):
        ModDef = SampleModDefDict[newSampleList[val]]
        for cond in [ConditionList1,ConditionList2,ConditionList3,ConditionList4,ConditionList5]:
            if(cond[0] == 'Code' or cond[0] == 'code'): ##assumes there is such a column that corresponds to the names on the Experiment DNA sample tab
                isthereCode = 1
                codename = cond[val+1]
                for mod in range(0,len(ModList)):
                    if codename == ModList[mod]:
                        displayID = newModList[mod]
                        test = ModDef.modules.create(displayID)
                        otherMD = ModDefDict[displayID]
                        test.definition = otherMD.identity
                        #should this be test.instance or test.definition or both?

    if isthereCode == 0:
        print('Error: There must be a column in the Experimental Conditions tab in the Samples sheet named "Code" that corresponds to the names of each Module in the Experimental DNA sample sheet.')
        return(-1)
    diditwork = 0
    return(diditwork)

"""""
COMPONENT DEFINITIONS
"""""
def CompMaker(PlasmidList_norepeat):
    CompDefDict = {}
    #creating ComponentDefinition for each plasmid type and adding description, key is the displayID and value is the CD
    for val in range(0,len(PlasmidList_norepeat)):
            displayID = PlasmidList_norepeat[val]
            temp = ComponentDefinition(displayID,BIOPAX_DNA) #encodes all plasmids as type BIOPAX_DNA
            CompDefDict[displayID] = temp

    for comp in CompDefDict:
        CompDefDict[comp].roles = SO_PLASMID
        doc.addComponentDefinition(CompDefDict[comp])
    return(CompDefDict)

"""""
FUNCTIONAL COMPONENTS + ANNOTATIONS
"""""
#creating FunctionalComponents for each plasmid present in each Module, and then adding the appropriate annotations

def FindMod(val,ExperimentSheet,ModList):
    for row in range(0,ExperimentSheet.nrows):
        for col in range(0,ExperimentSheet.ncols):
            cellvalue = (ExperimentSheet.cell(row,col)).value
            if cellvalue == ModList[val]: return (row,col)
    return(-1,-1)

def FuncMaker(newModList,ModList,ExperimentSheet,CompDefDict,ModDefDict,Unit):
    #FunCompDict = {}
    for val in range(0,len(ModList)):
        mod = newModList[val]
        (r,col) = FindMod(val,ExperimentSheet,ModList)
        r+=1
        endvar = 'b'
        while (r < ExperimentSheet.nrows and (ExperimentSheet.cell(r,0)).value != ''):
            if (ExperimentSheet.cell(r,0)).value in CompDefDict:
                displayId = (ExperimentSheet.cell(r,0)).value
                try:
                    temp = ModDefDict[mod].functionalComponents.create(displayId)
                    #FunCompDict[displayId+mod] = temp
                    temp.definition = (CompDefDict[displayId]).identity
                except:
                    displayId = displayId + endvar
                    endvar = chr(ord(endvar) + 1)
                    temp = ModDefDict[mod].functionalComponents.create(displayId)
                    #FunCompDict[displayId+mod] = temp
                    temp.definition = (CompDefDict[(displayId[:-1])]).identity
                (row,c) = DescriptionFinder('Plasmid Description',ExperimentSheet)
                descriptioncol = c
                PlasmidDescription = (ExperimentSheet.cell(r,descriptioncol)).value
                temp.description = PlasmidDescription
                temp.access = SBOL_ACCESS_PUBLIC
                temp.direction = SBOL_DIRECTION_NONE
                #setting annotations:
                valueURI = temp.identity + '#hasNumericalValue'
                value = (ExperimentSheet.cell(r,col)).value
                if value != '':
                    stringval = '%s' % float('%6g' % value)
                    #at most 6 significant figures
                    temp.setAnnotation(valueURI,stringval)
                    #temp.hasNumericalValue = FloatProperty(temp,'http://bu.edu/dasha/#hasNumericalValue','0','1')
                    #temp.hasNumericalValue = 10.0
                    unitsURI = temp.identity + '#hasUnit'
                    temp.setAnnotation(unitsURI,Unit)
            r+=1
    diditwork = 0
    return(diditwork)

#doc.write('JHT6_withSamples.xml')

#doc.write('dasha_testfile1_excel.xml')

#doc.write('test3.xml')

#add what the measure means!!
#make sure the unit property is getting the correct root

#put the whole spreadsheet into sbol
#figure out why names online in SynBioHub have the type beforehand


#for writing to synbiohub
#username = 'dveraksa@bu.edu'
#password = getpass.getpass(prompt='SynBioHub password:')

def UploadFunc(username,password,displayId,collectionname,collectiondescription):
    #ToImport = input('Do you want to save this collection to SynBioHub? (y/n) ')
    #if ToImport == 'y':
    shop = PartShop('https://synbiohub.org')
    shop.login(username, password)
    #answer = input('Do you want your collection to be named "{}"? (y/n) '.format(CollectionName))
    #if answer == 'y':
    # doc.displayId = CollectionName
        #has underscore attached to it
        #doc.name = CollectionName
        #in parenthesis
        #elif answer == 'n':
        #displayId = input('Enter collection displayID: ')
    #name = input('Enter collection name: ')
        #error--cant have displayID start with a number or contain spaces
    doc.displayId = displayId
    doc.name = collectionname
    #CollectionDescription = input('Enter collection description: ')
    doc.description = collectiondescription
    #0 = do not overwrite, 1 = overwrite, 2 = merge
    #the problem is that if you select overwrite but there is nothing to overwrite it doesn't add it regardless
        #overwrite = 2
    print(shop.submit(doc))
#    if result:
#        print("Success!")
#    else:
#        print(result)
    return(0)

#running it as it would be in the notebook:
#from sbol import *
#import re
#import sys
#import xlrd
#import getpass
#
#global doc
#doc = Document()
#setHomespace('http://bu.edu/dasha')
#Config.setOption('sbol_typed_uris',False)
#Config.setOption('sbol_compliant_uris',True)
#
#file_location = '20180606_JHT6.xlsm'
#
#wb = MakeBook(file_location)
#(ExpName, ExpSheet) = ExcelImport(wb)
#(Unit,CollectionName) = UnitCollectionFunc(ExpSheet)
#(ModList,PlasmidList_orig) = PlasModList(ExpSheet)
#PlasmidList_norepeat = PlasNoRepeat(PlasmidList_orig)
#NewModList = ModListCleaner(ModList,ExpName)
#ModDefDict = ModMaker(ExpSheet,ModList,NewModList)
#SamplesImport(ModList,NewModList,ModDefDict,wb,ExpName)
#
#
#username = 'dveraksa@bu.edu'
#password = getpass.getpass(prompt='SynBioHub password:')
#UploadFunc(username,password,displayId,collectionname,collectiondescription)
