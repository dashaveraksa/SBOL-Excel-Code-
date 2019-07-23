import experimentdnaexcel as pythonfile

testcounter = 0
file_location = 'SBOL_Sample_test.xlsm'
curfile = '20180618 JHT10.xlsm'
wb = pythonfile.MakeBook(curfile)
if wb:
    print('Test 1/10: opening file successful...')
    testcounter +=1

(ExpName, ExpSheet) = pythonfile.ExcelImport(wb)
if (ExpName,ExpSheet):
    print('Test 2/10: extracting Experiment Name, locating "Experiment DNA sample" successful...')
    testcounter +=1

Unit = pythonfile.UnitCollectionFunc(ExpSheet)
if Unit:
    print('Test 3/10: extracting unit successful...')
    testcounter +=1

(ModList,PlasmidList_orig) = pythonfile.PlasModList(ExpSheet)
if (ModList,PlasmidList_orig):
    print('Test 4/10: creating list of Modules and plasmids successful...')
    testcounter +=1

PlasmidList_norepeat = pythonfile.PlasNoRepeat(PlasmidList_orig)
if PlasmidList_norepeat:
    print('Test 5/10: creating non-repeating list of plasmids successful...')
    testcounter +=1

NewModList = pythonfile.ModListCleaner(ModList,ExpName)
if NewModList:
    print('Test 6/10: creating SBOL-compliant list of Modules successful...')
    testcounter +=1

ModDefDict = pythonfile.ModMaker(ExpSheet,ModList,NewModList)
if ModDefDict:
    print('Test 7/10: creating ModuleDefinitions and dictionary of Modules successful...')
    testcounter +=1

SamplesOutput = pythonfile.SamplesImport(ModList,NewModList,ModDefDict,wb,ExpName)
if SamplesOutput == 0:
    print('Test 8/10: creating Module Definitions for each Sample in the Samples tab, adding Annotations for each Experimental Condition successful...')
    testcounter +=1

CompDefDict = pythonfile.CompMaker(PlasmidList_norepeat)
if CompDefDict:
    print('Test 9/10: creating ComponentDefinition for each plasmid type and adding description successful...')
    testcounter +=1

FunctionalCompOutput = pythonfile.FuncMaker(NewModList,ModList,ExpSheet,CompDefDict,ModDefDict,Unit)
if FunctionalCompOutput == 0:
    print('Test 10/10: creating FunctionalComponents for each plasmid present in a Module, adding Annotations successful...')
    testcounter +=1

#ret = UploadFunc(username,password,projectID,projectName,projectDescription,experimentID,experimentName,experimentDescription,colURI)
#if ret #can be 0,1,or 2:

if testcounter == 10:
    print('All tests passed.')

#need to test all the upload functions
