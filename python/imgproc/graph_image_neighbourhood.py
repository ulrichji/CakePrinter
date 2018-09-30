import graph_provider

import image_file_loader
import image_scaler
import image_simple_grayscaler
import image_canny_binarizer

import numpy as np

class NodeIndexData(graph_provider.NodeData):
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def __str__(self):
		return str(self.x) + "," + str(self.y)

class GraphImageNeighbourhood(graph_provider.GraphProvider):
	def __init__(self, image_provider):
		self.image_provider = image_provider
	
	def getNeighbourIfNode(self, node, pos, node_image, image_shape):
		if(pos[0] >= 0 and pos[0] < image_shape[0] and pos[1] >= 0 and pos[1] < image_shape[1]):
			other = node_image[pos[0]][pos[1]]
			if(not other is None):
				return other
		return None
	
	def getNeighbours(self, pixel_pos, node_image, image_shape):
		y = pixel_pos[0]
		x = pixel_pos[1]
		node = node_image[y][x]
		neighbours = []
		
		other = self.getNeighbourIfNode(node, (y - 1, x - 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y - 1, x), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y - 1, x + 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y, x - 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y, x + 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y + 1, x - 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y + 1, x), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		other = self.getNeighbourIfNode(node, (y + 1, x + 1), node_image, image_shape)
		if(not other is None):
			neighbours.append(other)
		
		return neighbours
	
	def getGraph(self):
		provided_image = self.image_provider.getImage()
		possible_pixels = np.argwhere(provided_image > 0)
		
		node_image = [[None for x in range(provided_image.shape[1])] for y in range(provided_image.shape[0])]
		
		for pixel_pos in possible_pixels:
			node = graph_provider.Node()
			node_image[pixel_pos[0]][pixel_pos[1]] = node
		
		for pixel_pos in possible_pixels:
			neighbours = self.getNeighbours(pixel_pos, node_image, provided_image.shape)
			node = node_image[pixel_pos[0]][pixel_pos[1]]
			node.neighbours.extend(neighbours)
		
		node_list = []
		for pixel_pos in possible_pixels:
			node_list.append(node_image[pixel_pos[0]][pixel_pos[1]])
		
		graph = graph_provider.Graph()
		graph.node_list = node_list
		
		return graph
	

def main():
	file_image = image_file_loader.ImageFileLoader("examples/obama.jpg")
	scale_image = image_scaler.ImageScaler(file_image, (4000,4000))
	gray_image = image_simple_grayscaler.ImageSimpleGrayscaler(scale_image)
	binarized_image = image_canny_binarizer.ImageCannyBinarizer(gray_image, 100, 125, 3)
	
	neighbourhood_graph = GraphImageNeighbourhood(binarized_image)
	
	graph = neighbourhood_graph.getGraph()

if __name__ == "__main__":
	main()
