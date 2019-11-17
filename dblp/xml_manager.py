import json, xmltodict, collections, elasticsearch as es, time
from subprocess import check_output
from . import es_API

line_number = 0

def xmldictSpecialElementStringToObject(xml_dict, element_type):
    for key in xml_dict[element_type].keys():
        if key in ("author", "editor"):
            if isinstance(xml_dict[element_type][key], str):
                xml_dict[element_type][key] = [xml_dict[element_type][key]]

            for element in xml_dict[element_type][key]:
                if not isinstance(element, collections.OrderedDict):
                    # print(element)
                    index = xml_dict[element_type][key].index(element)                    
                    xml_dict[element_type][key][index] = collections.OrderedDict({"#text":element})
                    # print(xml_dict['article'][key][index])
    return xml_dict


def uploadElement(_es, xml_element, element_type):
    uploaded = False
    #print("\nXML input:")
    #print(xml_element)
    xml_dict = xmltodict.parse(xml_element.replace("&", "&amp;"))
    xml_dict = xmldictSpecialElementStringToObject(xml_dict, element_type)
    json_element = json.dumps(xml_dict, indent=4)
    print("JSON output:")
    print(json_element)
    #Store the document in Elasticsearch 
    try:
        uploaded = _es.index(index='dblp', body=json_element, id=xml_dict[element_type]["@key"])
    except es.exceptions.RequestError  as _e:
        uploaded = _e
    return uploaded


def wc(xml_file):
    return int(check_output(["wc", "-l", xml_file]).split()[0])


def getUploadPercentage(xml_file):
    total_line = wc(xml_file)
    global line_number
    percentage = 0
    while percentage <= 100:
        yield "data:" + str(percentage) + "\n\n"
        percentage = line_number/total_line*100
        time.sleep(0.5)
    return percentage

    
'''Read XMl file element by element for manage big XML file.'''
def readXML(xml_file, element_list, _es):
    xml = open(xml_file, "r")
    element_block_list = []
    element_block = []
    line = xml.readline().rstrip()
    element_type = ""

    while line:
        # Check if there's one of the element to search in line
        for element in element_list[:14]:
            if "<"+element in line:
                element_type = element
                break
        #print("Start block:")
        # Cycle on all line after main element that was found until close tag
        while "</"+element_type+">" not in line:
            #print(element_type, line)
            element_block.append(line)
            line = xml.readline().rstrip()

        #need to verify last line if it contains other element header after close tag
        if (len(line) - (line.find("</"+element_type+">") + len("</"+element_type+">"))) > 1:
            line = line.split("</"+element_type+">", 1)
            element_block.append(line[0]+"</"+element_type+">")
            line = line[1]
        else:
            element_block.append(line)
            #print(element_type, line)

        created = uploadElement(_es, "\n".join(element_block), element_type)
        global line_number
        line_number = xml.tell()
        element_block_list.append(element_block)
        element_block = []
        if "</" in line:
            line = xml.readline().rstrip()
    xml.close()
    