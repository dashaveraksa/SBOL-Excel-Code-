#Excel file name: 20180606_JHT6.xlsm
#Experiment DNA sample tab
#Collection: comerecombinase

from sbol import *
import re

"""""
EXCEL IMPORT
"""""

#testing excel import from Desktop
import xlrd

file_location = '20180618 JHT10.xlsm'
wb = xlrd.open_workbook(file_location)
#while 1:
#    mysheet = input("Enter sheet name: ")
#    try:
#        sheet = wb.sheet_by_name(mysheet)
#        break
#    except:
#        print(mysheet,'does not exist in the file.')

sheet = wb.sheet_by_name('Experiment DNA sample')

from xlrd.sheet import ctype_text

#searching for Experiment Name header in the first column of Experiment sheet, with the experiment name directly below it

NameSheet = wb.sheet_by_name('Experiment')
LookingFor = 'Experiment Name'

#error: need a sheet named Experiment

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

#finding unit and collection name -- watch out, there could be errors
Unit = ''
CollectionName = ''

for r in range(0,sheet.nrows):
    cell_obj = sheet.cell(r,0)
    if (cell_obj.value == 'Unit:' or cell_obj.value == 'Unit' or cell_obj.value == 'unit:' or cell_obj.value == 'unit'):
        Unit = (sheet.cell(r,1)).value
    elif (cell_obj.value == 'Collection:' or cell_obj.value == 'Collection' or cell_obj.value == 'collection:' or cell_obj.value == 'collection'):
        CollectionName = (sheet.cell(r,1)).value
    else:
        r+=1
if Unit == '':
    Unit = input('Unit not found. Enter it now: ')
if CollectionName == '':
    CollectionName = input('Collection Name not found. Enter it now: ')

#error: need Unit and Collection header in first column of datasheet

#creating a list of the plasmid numbers/module names
ModList = []
LookingFor = 'Plasmid Number'

for r in range(0,sheet.nrows):
    cell_obj = sheet.cell(r,0)
    if cell_obj.value == LookingFor:
        col = 1
        while (sheet.cell(r,col)).value != '' and (sheet.cell(r,col)).value != 'Plasmid Description':
            ModList.append(sheet.cell(r,col).value)
            col+=1
    else:
        r+=1

ModDescriptionList = ["5 ng Blank, 50 ng Blank","35 ng Blank, 20 ng LC41","45 ng Blank, 10 ng LC41","5 ng Blank, 50 ng LC20","15 ng Blank, 40 ng LC20","45 ng FlpO, 10 ng LC41"]

#creating a list of plasmids
PlasmidList_orig = []
for r in range(0,sheet.nrows):
    cell_obj = sheet.cell(r,0)
    if (cell_obj.value == LookingFor):
        r+=1
        while (r < sheet.nrows and (sheet.cell(r,0)).value != ''):
            PlasmidList_orig.append((sheet.cell(r,0)).value)
            r+=1

#takes away duplicates from PlasmidList_orig so that unique CD can be created
import collections
PlasmidList_norepeat = list(dict.fromkeys(PlasmidList_orig))

#finding column number with Plasmid Descriptions
def DescriptionFinder():
    for r in range(0,sheet.nrows):
        for c in range(0,sheet.ncols):
            cell_obj = sheet.cell(r,c)
            if cell_obj.value == 'Plasmid Description':
                return c

"""""
SBOL SETTINGS
"""""

doc = Document()
setHomespace('http://bu.edu/dasha')
Config.setOption('sbol_typed_uris',False)

"""""
MODULE DEFINITIONS
"""""

#this takes the module name/plasmid number and puts a '_' where the spaces are, then composes the ModuleNames into a new list
clean = lambda varStr: re.sub('\W|^(?=\d)','_', varStr)
newModList = [(ExperimentName + '_sample' + clean(ModName)) for ModName in ModList]

ModDefDict = {}
#this makes a dictionary with the key being the MD displayID and the value being the MD associated with that displayID, then adds appropriate description to each MD
for val in range(0,len(newModList)):
    displayID = newModList[val]
    temp = ModuleDefinition(displayID)
    ModDefDict[displayID] = temp
    #temp.description = ModDescriptionList[val]
    doc.addModuleDefinition(ModDefDict[displayID]) #ModDefDict[displayID] is of the type "MD"

"""""
COMPONENT DEFINITIONS
"""""

CompDefDict = {}
#creating ComponentDefinition for each plasmid type and adding description, key is the displayID and value is the CD
for val in range(0,len(PlasmidList_norepeat)):
        displayID = PlasmidList_norepeat[val]
        temp = ComponentDefinition(displayID,BIOPAX_DNA) #encodes all plasmids as type BIOPAX_DNA
        CompDefDict[displayID] = temp

for comp in CompDefDict:
    CompDefDict[comp].roles = SO_PLASMID
    doc.addComponentDefinition(CompDefDict[comp])

"""""
FUNCTIONAL COMPONENTS + ANNOTATIONS
"""""
#creating FunctionalComponents for each plasmid present in each Module, and then adding the appropriate annotations

def FindMod(val):
    for row in range(0,sheet.nrows):
        for col in range(0,sheet.ncols):
            cellvalue = (sheet.cell(row,col)).value
            if cellvalue == ModList[val]: return (row,col)

#FunCompDict = {}
for val in range(0,len(ModList)):
    mod = newModList[val]
    (r,col) = FindMod(val)
    r+=1
    endvar = 'b'
    while (r < sheet.nrows and (sheet.cell(r,0)).value != ''):
        if (sheet.cell(r,0)).value in CompDefDict:
            displayId = (sheet.cell(r,0)).value
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
            descriptioncol = DescriptionFinder()
            PlasmidDescription = (sheet.cell(r,descriptioncol)).value
            temp.description = PlasmidDescription
            temp.access = SBOL_ACCESS_PUBLIC
            temp.direction = SBOL_DIRECTION_NONE
            #setting annotations:
            valueURI = temp.identity + '#hasNumericalValue'
            value = (sheet.cell(r,col)).value
            if value != '':
                value = str(round(value))
                temp.setAnnotation(valueURI,value)
                unitsURI = temp.identity + '#hasUnit'
                temp.setAnnotation(unitsURI,Unit)
        r+=1

#doc.write('test.xml')

#doc.write('dasha_testfile1_excel.xml')

doc.write('test3.xml')

#add what the measure means!!
#make sure the unit property is getting the correct root

#put the whole spreadsheet into sbol
#figure out why names online in SynBioHub have the type beforehand


#for writing to synbiohub
ToImport = input('Do you want to save this collection to SynBioHub? (y/n) ')
if ToImport == 'y':
    import getpass
    igem = PartShop('https://synbiohub.org')
    username = input('SynBioHub username: ')
    password = getpass.getpass(prompt='SynBioHub password:' )
    igem.login(username, password)
    answer = input('Do you want your collection to be named "{}"? (y/n) '.format(CollectionName))
    if answer == 'y':
        doc.displayId = CollectionName
        #has underscore attached to it
        doc.name = CollectionName
        #in parenthesis
    elif answer == 'n':
        displayId = input('Enter collection displayID: ')
        name = input('Enter collection name: ')
        #error--cant have displayID start with a number
        doc.displayId = displayId
        doc.name = name
    doc.description = 'trying to see if i can upload things directly from python'
    result = igem.submit(doc)
    if result:
        print("Success!")
elif ToImport == 'n':
    import sys
    sys.exit()

