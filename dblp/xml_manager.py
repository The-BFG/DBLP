import json, xmltodict, collections, elasticsearch as es, time
from subprocess import check_output
from . import es_API

line_number = 0.00

def wc(xml_file):
    return float(check_output(["wc", "-l", xml_file]).split()[0])

def getUploadPercentage(xml_file):
    total_line = wc(xml_file)
    global line_number
    percentage = 0
    while percentage <= 100:
        yield "retry: 100\n"
        yield "data:" + str(percentage) + "\n\n"
        percentage = line_number/total_line*100.00
        print(str(line_number)+" / "+str(total_line)+" = "+str(percentage))
        time.sleep(0.5)
    return percentage


def xmldictSpecialElementStringToObject(xml_dict, element_type):
    # print("\n\n"+str(xml_dict))
    for key in xml_dict[element_type].keys():
        if key in ("author", "editor"):
            if isinstance(xml_dict[element_type][key], str):
                xml_dict[element_type][key] = [xml_dict[element_type][key]]
                # print(xml_dict[element_type][key])

            if not isinstance(xml_dict[element_type][key], collections.OrderedDict):
                for element in xml_dict[element_type][key]:
                    if not isinstance(element, collections.OrderedDict):
                        index = xml_dict[element_type][key].index(element)
                        xml_dict[element_type][key][index] = collections.OrderedDict({"#text":element})
                        # print(xml_dict[element_type][key][index])
    return xml_dict


def uploadElement(_es, xml_element, element_type, index_name='new_index'):
    uploaded = False
    # print("\nXML input:")
    # print(xml_element)
    xml_dict = xmltodict.parse(xml_element.replace("&", "&amp;"))
    xml_dict = xmldictSpecialElementStringToObject(xml_dict, element_type)
    json_element = json.dumps(xml_dict, indent=4)
    # print("JSON output:")
    # print(json_element)
    # Store the document in Elasticsearch 
    try:
        uploaded = _es.index(index=index_name, body=json_element, id=xml_dict[element_type]["@key"])
    except es.exceptions.RequestError  as _e:
        uploaded = _e
    return uploaded

    
'''Read XMl file element by element for manage big XML file.'''
def readXML(xml_file, element_list, _es, index_name):
    global line_number
    xml = open(xml_file, "r")
    element_block_list = []
    element_block = []
    line = xml.readline().rstrip()
    element_type = ""

    while line:
        # Check if there's one of the element to search in line
        if line.find("\n") == 0:
            line = xml.readline()
            line_number = line_number+1
            continue
        for element in element_list[:14]:
            if "<"+element in line:
                element_type = element
                break
        #print("Start block:")
        # Cycle on all line after main element that was found until close tag
        while "</"+element_type+">" not in line:
            # print(element_type, line)
            element_block.append(line)
            line = xml.readline().rstrip()
            line_number = line_number+1

        # Need to verify last line if it contains other element header after close tag
        if (len(line) - (line.find("</"+element_type+">") + len("</"+element_type+">"))) > 2:
            line = line.split("</"+element_type+">", 1)
            element_block.append(line[0]+"</"+element_type+">")
            # print(element_type, line[0]+"</"+element_type+">")
            line = line[1]
        else:
            element_block.append(line)
            # print(element_type, line)

        created = uploadElement(_es, "\n".join(element_block), element_type, index_name)

        # print(line_number)
        element_block_list.append(element_block)
        element_block = []
        if "</" in line:
            line = xml.readline()
            line_number = line_number+1

    xml.close()
    