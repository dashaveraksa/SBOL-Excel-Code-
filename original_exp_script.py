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

file_location = '20180606_JHT6.xlsm'
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


#finding unit
for r in range(0,sheet.nrows):
    cell_obj = sheet.cell(r,0)
    if (cell_obj.value == 'Unit:' or cell_obj.value == 'Unit'):
        break
    else:
        r+=1
if r == sheet.nrows:
    Unit = input('Unit not found. Enter it now: ')
else:
    Unit = (sheet.cell(r,1)).value

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
    if ((cell_obj.value)[0] == 'p' and (cell_obj.value)[1].isupper()): #pulls out anything in the first column that starts with 'p' and is followed by a capital letter
        #important to make sure that all plasmids have the 'p' in front because not all the ones on the data sheet do
        PlasmidList_orig.append(sheet.cell(r,0).value)

#takes away duplicates -- IMPORTANT NEED TO fix this later because otherwise the three different versions of pbw363 get deleted

####ACTUALLLYYYYYY the list with the copies still exists as PlasmidList_orig, just need to add 'a','b','c', etc to each

#the logic would be, "if duplicate, then add a to each instance
#PlasmidList_orig[4] + 'a')


from collections import OrderedDict
PlasmidList_norepeat = list(dict.fromkeys(PlasmidList_orig))

#finding the plasmid descriptions
PlasmidDescriptionList = ["CFP (pCAG-mRuby pKK205)", "IFP (TRE-BFP-from-BW2139? pKK372)", "OFP (FSF-GFP pKK370)", "pEF-rtTA (from-BW586?? pKK371)", "BLANK (Cag-FALSE pKK203)", "LC41 (pHR-hU6-shRNAFF4 pKK375)", "LC20 (pHR-U6/TetO-shRNA pKK374)", "TRE-FlpO-3xshFF4 (from-BW2909 pKK373)"]

#take out any repeats--my assumption here is that the same plasmid will have the same description

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
    temp.description = ModDescriptionList[val]
#this adds the MD to the document
    doc.addModuleDefinition(ModDefDict[displayID]) #ModDefDict[displayID] is of the type "MD"


##creating ModuleDefinition for 1:DNA X
#dnax = ModuleDefinition('DNA_X_1')
#doc.addModuleDefinition(dnax)
#dnax.description = "5 ng Blank, 50 ng Blank"
#
##creating ModuleDefinition for 2:DNA A
#dnaa = ModuleDefinition('DNA_A_2')
#doc.addModuleDefinition(dnaa)
#dnaa.description = "35 ng Blank, 20 ng LC41"
#
##creating ModuleDefinition for 3:DNA B
#dnab = ModuleDefinition('DNA_B_3')
#doc.addModuleDefinition(dnab)
#dnab.description = "45 ng Blank, 10 ng LC41"
#
##creating ModuleDefinition for 4:DNA C
#dnac = ModuleDefinition('DNA_C_4')
#doc.addModuleDefinition(dnac)
#dnac.description = "5 ng Blank, 50 ng LC20"
#
##creating ModuleDefinition for 5:DNA D
#dnad = ModuleDefinition('DNA_D_5')
#doc.addModuleDefinition(dnad)
#dnad.description = "15 ng Blank, 40 ng LC20"
#
##creating ModuleDefinition for 6:DNA E
#dnae = ModuleDefinition('DNA_E_6')
#doc.addModuleDefinition(dnae)
#dnae.description = "45 ng FlpO, 10 ng LC41"

"""""
COMPONENT DEFINITIONS
"""""
CompDefDict = {}
#creating ComponentDefinition for each plasmid type and adding description, key is the displayID and value is the CD
for val in range(0,len(PlasmidList_norepeat)):
    displayID = PlasmidList_norepeat[val]
    temp = ComponentDefinition(displayID,BIOPAX_DNA) ##encodes all plasmids as type BIOPAX_DNA
    CompDefDict[displayID] = temp
    temp.description = PlasmidDescriptionList[val]

#pbw465 = ComponentDefinition('pBW465',BIOPAX_DNA)
#pbw465.description = "CFP (pCAG-mRuby pKK205)"
#
#pbw2139 = ComponentDefinition('pBW2139',BIOPAX_DNA)
#pbw2139.description = "IFP (TRE-BFP-from-BW2139? pKK372)"
#
#pbw339 = ComponentDefinition('pBW339',BIOPAX_DNA)
#pbw339.description = "OFP (FSF-GFP pKK370)"
#
#pbw586 = ComponentDefinition('pBW586',BIOPAX_DNA)
#pbw586.description = "pEF-rtTA (from-BW586?? pKK371)"
#
#pbw363 = ComponentDefinition('pBW363',BIOPAX_DNA)
#pbw363.description = "BLANK (Cag-FALSE pKK203)"
#
#plc41 = ComponentDefinition('pLC41',BIOPAX_DNA)
#plc41.description = "LC41 (pHR-hU6-shRNAFF4 pKK375)"
#
#plc20 = ComponentDefinition('pLC20',BIOPAX_DNA)
#plc20.description = "LC20 (pHR-U6/TetO-shRNA pKK374)"

#pbw2909 = ComponentDefinition('pBW2909',BIOPAX_DNA)
#pbw2909.description = "TRE-FlpO-3xshFF4 (from-BW2909 pKK373)"

#assigning role of PLASMID to each ComponentDefinition, adding all
#definitions to the Document
for comp in CompDefDict:
    CompDefDict[comp].roles = SO_PLASMID
    doc.addComponentDefinition(CompDefDict[comp])
    
for mod in ModDefDict:
    for num in range(0,len(PlasmidList_norepeat)):
            displayId = PlasmidList_norepeat[num]
            temp = ModDefDict[mod].functionalComponents.create(displayId)
            temp.definition = (CompDefDict[displayId]).identity
            temp.description = (CompDefDict[displayId]).description

##^above only includes one copy of the pbw363, cant figure out how to make three different ones

"""""
FUNCTIONAL COMPONENTS
"""""
#
#FuncCompDict = {}
#for mod in ModDefDict:
#    for num in range(0,len(PlasmidList_norepeat)):
#        temp = ModDefDict[mod].functionalComponents.create(PlasmidList_norepeat[num])
#        temp.definition = .identity
#        temp.description = (PlasmidList_norepeat[num]).description

    #
#    #creating 3 FunctionalComponents for PBW363
#    fcp363a = ModDefDict[mod].functionalComponents.create('pbw363a')
#    fcp363a.definition = pbw363.identity
#    fcp363a.description = pbw363.description
#
#    #look up -- do you need both the description and the definition??
#
#    fcp363b = ModDefDict[mod].functionalComponents.create('pbw363b')
#    fcp363b.definition = pbw363.identity
#    fcp363b.description = pbw363.description
#    fcp363c = ModDefDict[mod].functionalComponents.create('pbw363c')
#    fcp363c.definition = pbw363.identity
#    fcp363c.description = pbw363.description
#
#    #creating FunctionalComponents for the rest of the plasmids
#    fcp465 = ModDefDict[mod].functionalComponents.create('pbw465')
#    fcp465.definition = pbw465.identity
#    fcp465.description = pbw465.description
#
#    fcp2139 = ModDefDict[mod].functionalComponents.create('pbw2139')
#    fcp2139.definition = pbw2139.identity
#    fcp2139.description = pbw2139.description
#
#    fcp339 = ModDefDict[mod].functionalComponents.create('pbw339')
#    fcp339.definition = pbw339.identity
#    fcp339.description = pbw339.description
#
#    fcp586 = ModDefDict[mod].functionalComponents.create('pbw586')
#    fcp586.definition = pbw586.identity
#    fcp586.description = pbw586.description
#
#    fcp41 = ModDefDict[mod].functionalComponents.create('plc41')
#    fcp41.definition = plc41.identity
#    fcp41.description = plc41.description
#
#    fcp20 = ModDefDict[mod].functionalComponents.create('plc20')
#    fcp20.definition = plc20.identity
#    fcp20.description = plc20.description
#
#    fcp2909 = ModDefDict[mod].functionalComponents.create('pbw2909')
#    fcp2909.definition = pbw2909.identity
#    fcp2909.description = pbw2909.description
#
#    #defining access and direction for all FunctionalComponents, adding a hasUnit Annotation to each
#    for j in [fcp465, fcp2139, fcp339, fcp586, fcp41, fcp20, fcp2909, fcp363a, fcp363b, fcp363c]:
#        j.access = SBOL_ACCESS_PUBLIC
#        j.direction = SBOL_DIRECTION_NONE

doc.write('test.xml')

"""""
ANNOTATIONS and MEASUREMENTS
"""""

#for val in range(0,len(ModList)):


#adding Annotation for each FunctionalComponent and setting its value,
#valueURI = fcp465.identity + '#hasNumericalValue'
#fcp465.setAnnotation(valueURI,"25")
#unitsURI = fcp465.identity + '#hasUnit'
#fcp465.setAnnotation(unitsURI,"nanograms")
#typesURI = fcp465.identity + '#types'
#
#""""IMPORTANT SEE ABOVE^^^^^^^^
#    """""
#
#valueURI = fcp2139.identity + '#hasNumericalValue'
#fcp2139.setAnnotation(valueURI,"50")
#unitsURI = fcp2139.identity + '#hasUnit'
#fcp2139.setAnnotation(unitsURI,"nanograms")
#
#valueURI = fcp339.identity + '#hasNumericalValue'
#fcp339.setAnnotation(valueURI,"50")
#unitsURI = fcp339.identity + '#hasUnit'
#fcp339.setAnnotation(unitsURI,"nanograms")
#
#valueURI = fcp586.identity + '#hasNumericalValue'
#fcp586.setAnnotation(valueURI,"50")
#unitsURI = fcp586.identity + '#hasUnit'
#fcp586.setAnnotation(unitsURI,"nanograms")
#
#valueURI = fcp363a.identity + '#hasNumericalValue'
#fcp363a.setAnnotation(valueURI,"5")
#unitsURI = fcp363a.identity + '#hasUnit'
#fcp363a.setAnnotation(unitsURI,"nanograms")
#
#valueURI = fcp363b.identity + '#hasNumericalValue'
#fcp363b.setAnnotation(valueURI,"50")
#unitsURI = fcp363b.identity + '#hasUnit'
#fcp363b.setAnnotation(unitsURI,"nanograms")
#
#valueURI = fcp363c.identity + '#hasNumericalValue'
#fcp363c.setAnnotation(valueURI,"20")
#unitsURI = fcp363c.identity + '#hasUnit'
#fcp363c.setAnnotation(unitsURI,"nanograms")

#doc.write('dasha_testfile1_excel.xml')

#add what the measure means!!
#make sure the unit property is getting the correct root

#put the whole spreadsheet into sbol
#figure out why names online in SynBioHub have the type beforehand

