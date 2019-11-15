import json, xmltodict, elasticsearch as es
import collections

xml_element = '<article mdate="2017-06-09" key="persons/CasperGGGHLR12"><author orcid="0000-0002-1163-8988">Markus Casper</author><author>Gayane Grigoryan</author><author>Oliver Gronz</author><author>Oliver Gutjahr</author><author orcid="0000-0002-4831-9016">G&uuml;nther Heinemann</author><author>Rita Ley</author><author>Andreas Rock</author><title>Analysis of projected hydrological behavior of catchments based on signature indices</title><journal>Hydrology and Earth System Sciences</journal><volume>16</volume><pages>409-421</pages><year>2012</year><ee>https://doi.org/10.5194/hess-16-409-2012</ee></article>'
xml_dict = xmltodict.parse(xml_element.replace("&", "&amp;"))
print(xml_dict['article'])
# for key in xml_dict['article'].keys():
#     for element in xml_dict['article'][key]:
#         print(type(element))
#         if type(element) is collections.OrderedDict:
#             print("dentro")
#             subelement = ""
#             for key in element.keys():
#                 subelement = subelement+key+":"+element[key]+" "
#             print(subelement)


for key in xml_dict['article'].keys():
    if key in ("author", "editor"):
        for element in xml_dict['article'][key]:
            if not isinstance(element, collections.OrderedDict):
                print(element)
                index = xml_dict['article'][key].index(element)
                xml_dict['article'][key][index] = collections.OrderedDict({"#text":element})
                print(xml_dict['article'][key][index])
