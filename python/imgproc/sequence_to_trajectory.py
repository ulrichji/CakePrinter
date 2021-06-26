import image_file_loader
import image_scaler
import image_simple_grayscaler
import image_canny_binarizer
import graph_image_neighbourhood
import graph_to_sequence
import graph_provider

import numpy as np
import scipy.sparse.csgraph as scipycsgraph

class SequenceToTrajectory:
	def __init__(self, sequence_provider):
		self.sequence_provider = sequence_provider
	
	def generateSectionIndices(self, section):
		for i,node in enumerate(section):
			node.data.index = i
	
	def generateSectionDistanceMatrix(self, section):
		distance_matrix = np.full((len(section), len(section)), np.inf)
		
		for node in section:
			distance_matrix[node.data.index][node.data.index] = 0
			for edge in node.neighbours:
				source_index = node.data.index
				dest_index = edge.dest.data.index
				edge_weight = edge.weight
				
				distance_matrix[source_index][dest_index] = edge_weight
		
		return distance_matrix
	
	#Simple implementation of floyd warshall
	def getShortestDistancePairs(self, distance_matrix):
		pure_distance_matrix = np.array(distance_matrix)
		
		return scipycsgraph.shortest_path(pure_distance_matrix, return_predecessors=True, method='D')
		
		#n = len(distance_matrix) #The matix is square
		#for k in range(n):
		#	for i in range(n):
		#		for j in range(n):
		#			if(distance_matrix[i][j][0] > distance_matrix[i][k][0] + distance_matrix[k][j][0]):
		#				new_distance = distance_matrix[i][k][0] + distance_matrix[k][j][0]
		#				new_predecessor = distance_matrix[k][j][1]
		#				distance_matrix[i][j] = (new_distance, new_predecessor)
	
	def generateTrajectoryFromDistanceMatrix(self, distance_matrix, predecessors):
		longest_span = 0
		longest_span_pos = (0,0)
		n = len(distance_matrix)
		
		for i in range(n):
			for j in range(n):
				dist = distance_matrix[i][j]
				if(dist > longest_span):
					longest_span = dist
					longest_span_pos = (i,j)
		
		trajectory = []
		current_index = longest_span_pos[1]
		trajectory.append(current_index)
		while(current_index != longest_span_pos[0]):
			current_index = predecessors[longest_span_pos[0]][current_index]
			trajectory.append(current_index)
		
		return trajectory
	
	def getTrajectoryNodes(self, trajectory, section):
		trajectory_nodes = []
		non_trajectory_nodes = []
		keep_index = [False for i in range(len(section))]
		
		for index in trajectory:
			keep_index[index] = True
			trajectory_nodes.append(section[index])
		
		for i in range(len(section)):
			if(not keep_index[i]):
				non_trajectory_nodes.append(section[i])
		
		return trajectory_nodes, non_trajectory_nodes
	
	
	def updateEdges(self, section):
		for node in section:
			new_neighbours = []
			for edge in node.neighbours:
				if(edge.dest in section):
					new_neighbours.append(edge)
			
			node.neighbours.clear()
			node.neighbours = new_neighbours
	
	def getTrajectoryFromSection(self, section):
		print("Indices of "+str(len(section))+" elements")
		self.generateSectionIndices(section)
		
		print("Distance matrix")
		distance_matrix = self.generateSectionDistanceMatrix(section)
		print("Shortest distance")
		distance_matrix, predecessors = self.getShortestDistancePairs(distance_matrix)
		
		print("Trajectory")
		trajectory = self.generateTrajectoryFromDistanceMatrix(distance_matrix, predecessors)
		
		print("Trajectory extraction")
		trajectory_nodes, remaining_nodes = self.getTrajectoryNodes(trajectory, section)
		print("Update edges")
		self.updateEdges(remaining_nodes)
		self.updateEdges(trajectory_nodes)
		
		print("Graph")
		graph = graph_provider.Graph()
		graph.node_list = remaining_nodes
		print("Remaining")
		remaining_set = graph_to_sequence.getSequencesFromGraph(graph)
		
		return trajectory_nodes, remaining_set
	
	def getTrajectories(self):
		sections = self.sequence_provider.getSequences()
		trajectories = []
		
		while(len(sections) > 0):
			print(str(len(sections)) +" sections left")
			section = sections.pop(0)
			trajectory, new_sections = self.getTrajectoryFromSection(section)
			sections.extend(new_sections)
			trajectories.append(trajectory)
		
		return trajectories

def getPositionsFromTrajectory(trajectory):
	positions = []
	for node in trajectory:
		position = (node.data.x, node.data.y)
		positions.append(position)
	
	return positions

def savePositions(file_path, positions_list):
	f = open(file_path, "w")
	
	f.write('\n'.join([','.join(["("+str(pos[0]) + "," + str(pos[1]) + ")" for pos in pos_trajectory]) for pos_trajectory in positions_list]))
	
	f.close()

def main():
	file_image = image_file_loader.ImageFileLoader("examples/zivid.png")
	scale_image = image_scaler.ImageScaler(file_image, (4600,4600))
	gray_image = image_simple_grayscaler.ImageSimpleGrayscaler(scale_image)
	binarized_image = image_canny_binarizer.ImageCannyBinarizer(gray_image, 100, 125, 3)
	
	neighbourhood_graph = graph_image_neighbourhood.GraphImageNeighbourhood(binarized_image)
	sections_data = graph_to_sequence.GraphToSequence(neighbourhood_graph)
	trajectories_provider = SequenceToTrajectory(sections_data)
	trajectories = trajectories_provider.getTrajectories()
	
	positions_list = []
	for trajectory in trajectories:
		positions = getPositionsFromTrajectory(trajectory)
		positions_list.append(positions)
	
	savePositions("zivid_pos_trajectory.txt", positions_list)

if __name__ == "__main__":
	main()
