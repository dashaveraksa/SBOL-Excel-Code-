import sbol
sbol.testSBOL()

from sbol import *
doc = Document()
doc.read('crispr_example.xml')
doc.write('crispr_example_out.xml')
len(doc)
print(doc)

for obj in doc:
    print(obj)

setHomespace('http://sbols.org/CRISPR_Example')
Config.setOption('sbol_compliant_uris', False)
Config.setOption('sbol_typed_uris', False)
crispr_template = ModuleDefinition('CRISPR_Template')
print(crispr_template)

cas9 = ComponentDefinition('Cas9', BIOPAX_PROTEIN)
target_promoter = ComponentDefinition('target_promoter')

doc.addModuleDefinition(crispr_template)
doc.addComponentDefinition(cas9)
crispr_template = doc.getModuleDefinition('http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0')
cas9 = doc.getComponentDefinition('http://sbols.org/CRISPR_Example/cas9_generic/1.0.0')

Config.setOption('sbol_compliant_uris', True)
Config.setOption('sbol_typed_uris', False)
crispr_template = doc.moduleDefinitions['CRISPR_Template']
cas9 = doc.componentDefinitions['cas9_generic']

