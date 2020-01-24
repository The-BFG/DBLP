import json, xmltodict, collections, elasticsearch as es, time
from elasticsearch import helpers
from subprocess import check_output

line_number = 0.00

def wc(xml_file):
    return float(check_output(["wc", "-l", xml_file]).split()[0])


def getUploadPercentage(xml_file):
    total_line = wc(xml_file)
    global line_number
    if line_number == total_line:
        line_number = 0
    percentage = 0
    while percentage <= 100:
        yield "retry: 100\n"
        yield "data:" + str(percentage) + "\n\n"
        percentage = line_number/total_line*100.00
        print(str(line_number)+" / "+str(total_line)+" = "+str(percentage))
        time.sleep(1)
    return percentage


def xmldictSpecialElementStringToObject(xml_dict, element_type):
    #print("\n\n"+str(xml_dict))
    for key in xml_dict[element_type].keys():
        if "@" not in key and key != "i":
            if isinstance(xml_dict[element_type][key], str):
                xml_dict[element_type][key] = [xml_dict[element_type][key]]
                #print(xml_dict[element_type][key])

            if not isinstance(xml_dict[element_type][key], collections.OrderedDict):
                for element in xml_dict[element_type][key]:
                    if not isinstance(element, collections.OrderedDict):
                        index = xml_dict[element_type][key].index(element)
                        xml_dict[element_type][key][index] = collections.OrderedDict({"#text":element})
                        #print(xml_dict[element_type][key][index])
                        #print(xml_dict)
    return xml_dict


def createJsonElement(xml_element, element_type, index_name='new_index'):
    #print("\nXML input:")
    #print(xml_element)
    try:
        xml_dict = xmltodict.parse(xml_element.replace("&", "&amp;"))
        xml_dict = xmldictSpecialElementStringToObject(xml_dict, element_type)
        xml_dict = collections.OrderedDict({
            "_index" : index_name,
            "_doc" : element_type,
            "_id" : xml_dict[element_type]["@key"],
            "_source" : xml_dict
        })
    except Exception as e:
        print(e)
        xml_dict = {}
    return xml_dict

    
def uploadMultiJson(_es, json_list, index_name):
    try:
        status, _ = helpers.bulk(_es, json_list, index=index_name)
        print("Upload result:", status)
    except Exception as e:
        print("\nBULK UPLOAD ERROR:", e)
    return


'''Read XMl file element by element for manage big XML file.'''
def readXML(xml_file, element_list, _es, index_name):
    global line_number
    counter = 0
    xml = open(xml_file, "r")
    json_list = []
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

        element_block = "\n".join(element_block)
        element_block = element_block.replace("<sup>", "&lt;sup&gt;")
        element_block = element_block.replace("</sup>", "&lt;/sup&gt;")
        element_block = element_block.replace("<sub>", "&lt;sub&gt;")
        element_block = element_block.replace("</sub>", "&lt;/sub&gt;")
        element_block = element_block.replace("<i>", "&lt;i&gt;")
        element_block = element_block.replace("</i>", "&lt;/i&gt;")
        element_block = element_block.replace("<tt>", "&lt;tt&gt;")
        element_block = element_block.replace("</tt>", "&lt;/tt&gt;")
        element_block = element_block.replace("<ref>", "&lt;ref&gt;")
        element_block = element_block.replace("</ref>", "&lt;/ref&gt;")
        xml_dict = createJsonElement(element_block, element_type, index_name=index_name)

        if "</" in line:
            line = xml.readline()
            line_number = line_number+1

        if  counter == 5000:
            #print(json_list)
            uploadMultiJson(_es, json_list, index_name=index_name)
            json_list = []
            if xml_dict:
                json_list.append(xml_dict)
            counter = 0
            counter = counter+1
        else:
            if xml_dict:
                json_list.append(xml_dict)
            counter = counter+1
        element_block = []

    if json_list:
        uploadMultiJson(_es, json_list, index_name=index_name)

    xml.close()
    