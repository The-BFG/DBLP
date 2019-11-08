'''Read an element block with all its subelement.'''
def read_element():
    block = []


    return block

'''Read XMl file element by element for manage big XML file.'''
def readXML(xml_file, element_list):
    xml = open(xml_file, "r")
    element_block_list = []
    element_block = []
    line = xml.readline().rstrip()
    element_type = ""

    while line:
        # Check if there's one of the element to search in line
        for element in element_list:
            if element in line:
                element_type = element           
        print("Start block:")
        # Cycle on all line after main element that was found until close tag
        while "</"+element_type not in line:
            print(element_type, line)
            element_block.append(line)
            line = xml.readline().rstrip()

        #need to verify last line if it contains other element header after close tag
        if (len(line) - (line.find("</"+element_type+">") + len("</"+element_type+">"))) > 2:
            line = line.split("</"+element_type+">", 1)
            element_block.append(line[0])
            line = line[1]
        else:
            element_block.append(line)
            print(element_type, line)
        element_block_list.append(element_block)
        element_block = []
        print("Endblock\n")
        if "</" in line:
            line = xml.readline().rstrip()

    for block in element_block_list:
        print(block)
    xml.close()
    return element_block_list