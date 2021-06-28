import image_file_loader
import image_scaler
import image_simple_grayscaler
import image_canny_binarizer
import graph_image_neighbourhood

def getSequenceFromNode(node):
	queue = [node]
	sequence = [node]
	
	node.data.visited=True
	while(len(queue) > 0):
		node = queue.pop(0)
		for edge in node.neighbours:
			if(not edge.dest.data.visited):
				edge.dest.data.visited = True
				queue.append(edge.dest)
				sequence.append(edge.dest)
	
	return sequence


def getSequencesFromGraph(graph):
	sequences = []
	
	for node in graph.node_list:
		node.data.visited = False
	
	list_index = 0
	while(list_index < len(graph.node_list)):
		node = graph.node_list[list_index]
		if(not node.data.visited):
			sequence = getSequenceFromNode(node)
			sequences.append(sequence)
		list_index += 1
	
	return sequences

class NodeWrapper:
	def __init__(self, node):
		self.node = node
	
	def __lt__(self, other):
		return self.node.data.distance < other.data.distance

#Class for gettings trajectory sequences from a graph
class GraphToSequence:
	def __init__(self, graph_provider):
		self.graph_provider = graph_provider
	
	def getSequences(self):
		return getSequencesFromGraph(self.graph_provider.getGraph())

import sys
def main():
	if len(sys.argv) <= 1:
		print('Usage: python {} <file to load>'.format(sys.argv[0]))
		return

	file_path = sys.argv[1]
	file_image = image_file_loader.ImageFileLoader(file_path)
	scale_image = image_scaler.ImageScaler(file_image, (4000,4000))
	gray_image = image_simple_grayscaler.ImageSimpleGrayscaler(scale_image)
	binarized_image = image_canny_binarizer.ImageCannyBinarizer(gray_image, 100, 125, 3)
	
	neighbourhood_graph = graph_image_neighbourhood.GraphImageNeighbourhood(binarized_image)
	sections_data = GraphToSequence(neighbourhood_graph)
	sections = sections_data.getSequences()

	print('Created a sequence of {} sections'.format(len(sections)))
	print('The following list contains the lengths of the sections:')
	print(' ' + '\n '.join(str(i) + ': ' + str(len(s)) for i,s in enumerate(sections)))
	
if __name__ == "__main__":
	main()
