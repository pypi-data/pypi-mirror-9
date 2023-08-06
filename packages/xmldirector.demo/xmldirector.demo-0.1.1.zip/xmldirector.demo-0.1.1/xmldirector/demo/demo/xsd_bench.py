import lxml.etree
import time


for name in (
        'bible.xsd',
        'mods-3-0.xsd',
        'mods-3-1.xsd',
        'mods-3-2.xsd',
        'mods-3-3.xsd',
        'mods-3-4.xsd',
        'mods-3-5.xsd',
        'play.xsd'):
    print '-'*80
    print name
    ts = time.time()
    fp = open(name, 'rb')
    schema_doc = lxml.etree.XML(fp.read())
    print time.time() - ts
    validator = lxml.etree.XMLSchema(schema_doc)
    print time.time() - ts
