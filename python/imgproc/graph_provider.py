#Just a whatever data storage class
class NodeData:
	def __str__(self):
		return "nodata"

class Edge:
	def __init__(self, from_node, to_node, weight=1):
		self.source = from_node
		self.dest = to_node
		self.weight = weight

glob_index = 0
class Node:
	def __init__(self):
		global glob_index
		
		self.neighbours = []
		self.data = NodeData()
		self.index = glob_index
		glob_index += 1
	
	def __str__(self):
		return "[Node " + self._internalName() + " ==>  [" + ', '.join([edge.dest._internalName() for edge in self.neighbours]) + "]" + ", data:[" + str(self.data) + "]]"
	
	def _internalName(self):
		return str(self.index)
	
class Graph:
	def __init__(self):
		self.node_list = []

class GraphProvider:
	def getGraph(self):
		raise Exception("Graph provider must be inherited.")

