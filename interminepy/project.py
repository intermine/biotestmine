import collections

from lxml import etree


class Project:
    def __init__(self, input):
        self.sources = collections.OrderedDict()

        parser = etree.XMLParser(remove_blank_text=True)
        self._projectTree = etree.parse(input, parser)

        for source_elem in self._projectTree.xpath('/project/sources/source'):
            self.sources[source_elem.attrib['name']] = Source(source_elem)


class Source:
    def __init__(self, elem):
        attrib = elem.attrib

        self.name = attrib['name']
        self.type = attrib['type']

        if 'dump' in attrib:
            self.dump = attrib['dump']
        else:
            self.dump = False
