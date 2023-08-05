################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree

XSI = "http://www.w3.org/2001/XMLSchema-instance"
XS = '{http://www.w3.org/2001/XMLSchema}'



SCHEMA_TEMPLATE = """<?xml version = "1.0" encoding = "UTF-8"?>
<xs:schema xmlns="http://dummy.libxml2.validator"
targetNamespace="http://dummy.libxml2.validator"
xmlns:xs="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
version="1.0"
elementFormDefault="qualified"
attributeFormDefault="unqualified">
</xs:schema>"""

def validate_xml(xml):
    """Validate an XML file represented as string. Follow all schemaLocations.

    :param xml: XML represented as string.
    :type xml: str
    """

    tree = lxml.etree.XML(xml)
    # Find all unique instances of 'xsi:schemaLocation="<namespace> <path-to-schema.xsd> ..."'
    schema_locations = set(tree.xpath("//*/@xsi:schemaLocation", namespaces={'xsi': XSI}))
    for schema_location in schema_locations:
        # Split namespaces and schema locations ; use strip to remove leading
        # and trailing whitespace.
        namespaces_locations = schema_location.strip().split()
        # Import all found namspace/schema location pairs
        for namespace, location in zip(*[iter(namespaces_locations)] * 2):
            schema_doc = lxml.etree.parse(open(location, 'rb').read())
            xmlschema = lxml.etree.XMLSchema(schema_doc)
            xmlschema.validate(tree)

