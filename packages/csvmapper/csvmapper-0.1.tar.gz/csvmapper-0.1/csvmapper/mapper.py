import json
import xml.etree.ElementTree as ET

""" Mapper base object """
class Mapper(object):
	def __init__(self):
		super(Mapper, self).__init__()

	def getRecords(self):
		pass

""" XML Mapper """
class XMLMapper(Mapper):
	""" An XML-Defined Mapper File for the CSV Parser"""
	def __init__(self, path):
		super(Mapper, self).__init__()
		self.path = path
		self.records = []

	# create a record from an element
	def createRecord(self, elem):
		recs = []
		for x in elem:
			rec = {}
			for a in x.attrib:
				rec[a] = x.attrib[a]
			recs.append(rec)
		return recs

	# parse the mapper
	def parseFile(self):
		tree = ET.parse(self.path)
		root = tree.getroot()
		j = len(root)
		while j > 0:
			j=j-1
			g = root[j]
			for record in g:
				self.records.append(self.createRecord(record))

	def getRecords(self):
		self.parseFile()
		return self.records


""" Uses a python dictionary as mapper file"""
class DictMapper(Mapper):
	def __init__(self):
		super(Mapper, self).__init__()
		self.dictionary = d

	def getRecords(self):
		self.records = self.dictionary

""" JSON Based Mapper """
class JSONMapper(Mapper):
	def __init__(self, jsonFile):
		self.jsonFile = jsonFile
		super(Mapper, self).__init__()

	def parse(self, jFile):
		fs = open(jFile)
		jt = fs.read()
		return json.loads(jt)

	def getRecords(self):
		self.records = self.parse(self.jsonFile)

# Test File
def test(m):
	m.getRecords()
	for rec in m.records:
		print rec

if __name__ == '__main__':
	m = XMLMapper('../mapper-example.xml')
	test(m)