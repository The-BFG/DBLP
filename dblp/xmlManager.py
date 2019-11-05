import xml.dom.minidom

def readXML(xml_file):
    dom = xml.dom.minidom.parse(xml_file)
    rootel = dom.documentElement
    print(rootel.nodeName)   # print root element name
    print(rootel.nodeType)
    topnodes = rootel.childNodes
    for toplevel in topnodes:
        print(toplevel.nodeName)     # print root children names
        print(toplevel.nodeType)
    return rootel