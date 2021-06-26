import math

def line(x0, y0, x1, y1):
    "Bresenham's line algorithm"
    return_pos_list = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            return_pos_list.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            return_pos_list.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy        
    return_pos_list.append((x, y))
    return return_pos_list

def optimizeTrajectory(positions, start_position=(0,0), end_position=(0,0)):
	number_of_positions = len(positions)
	current_position = start_position
	visited_positions = [False for i in range(len(positions))]
	order_indices = []
	
	for i in range(number_of_positions):
		shortest_distance = float('inf')
		shortest_index = 0
		for j in range(number_of_positions):
			if(visited_positions[j] == False):
				distance = math.sqrt(((positions[j][0][0] - current_position[0])**2) + ((positions[j][0][1] - current_position[1])**2))
				if(distance < shortest_distance):
					shortest_distance = distance
					shortest_index = j
		
		visited_positions[shortest_index] = True
		current_position = positions[shortest_index][1]
		order_indices.append(shortest_index)
	
	return order_indices

def fillTrajectories(trajectories):
	positions = []
	for trajectory in trajectories:
		if(len(trajectory) > 0):
			start_pos = trajectory[0]
			end_pos = trajectory[len(trajectory)-1]
			positions.append((start_pos, end_pos))
	
	optimized_position_indices = optimizeTrajectory(positions)
	combined_trajectory = []
	current_pos = (0,0)
	for indices in optimized_position_indices:
		draw_trajectory = trajectories[indices]
		start_pos = draw_trajectory[0]
		nodraw_trajectory = line(current_pos[0], current_pos[1], start_pos[0], start_pos[1])
		
		diffs = [abs(nodraw_trajectory[i+1][0] - nodraw_trajectory[i][0]) for i in range(len(nodraw_trajectory)-1) if abs(nodraw_trajectory[i+1][0] - nodraw_trajectory[i][0]) > 1]
		if(len(diffs) > 0):
			print(diffs)
		diffs = [abs(nodraw_trajectory[i+1][1] - nodraw_trajectory[i][1]) for i in range(len(nodraw_trajectory)-1) if abs(nodraw_trajectory[i+1][1] - nodraw_trajectory[i][1]) > 1]
		if(len(diffs) > 0):
			print(diffs)
		diffs = [abs(draw_trajectory[i+1][0] - draw_trajectory[i][0]) for i in range(len(draw_trajectory)-1) if abs(draw_trajectory[i+1][0] - draw_trajectory[i][0]) > 1]
		if(len(diffs) > 0):
			print(diffs)
		diffs = [abs(draw_trajectory[i+1][1] - draw_trajectory[i][1]) for i in range(len(draw_trajectory)-1) if abs(draw_trajectory[i+1][1] - draw_trajectory[i][1]) > 1]
		if(len(diffs) > 0):
			print(diffs)
		
		combined_trajectory.extend([(pos[0], pos[1], 0) for pos in nodraw_trajectory])
		combined_trajectory.extend([(pos[0], pos[1], 1) for pos in draw_trajectory])
		
		current_pos = draw_trajectory[len(draw_trajectory)-1]
	
	return combined_trajectory

def getStepsFromPosTrajectory(pos_trajectory):
	step_trajectory = []
	
	if(len(pos_trajectory) <= 1):
		return (0,0,0)
	
	current_pos = pos_trajectory[0]
	for pos in pos_trajectory[1:]:
		x_diff = pos[0] - current_pos[0]
		y_diff = pos[1] - current_pos[1]
		draw = pos[2]
		current_pos = pos
		
		x_step = 0
		y_step = 0
		if(x_diff > 0):
			x_step = 1
		elif(x_diff < 0):
			x_step = -1
		if(y_diff > 0):
			y_step = 1
		elif(y_diff < 0):
			y_step = -1
		
		#if(abs(x_diff) > 1 or abs(y_diff) > 1):
		#	print(x_diff, y_diff)
		
		step_trajectory.append((x_step, y_step, draw))

	return step_trajectory

def main():
	pos_trajectories = []
	
	f = open("zivid_pos_trajectory.txt", "r")
	
	prev_x = 0
	prev_y = 0
	
	for line in f:
		positions = []
		prev_x = None
		prev_y = None
		while(len(line) > 0):
			pos_start = line.find("(")
			pos_end = line.find(")", pos_start)
			if(pos_start >= 0 and pos_end >= 0):
				pos_text = line[pos_start+1 : pos_end]
				values = pos_text.split(",")
				x = int(values[0])
				y = int(values[1])
				line = line[pos_end+1:].strip()
				
				if(not prev_x is None and not prev_y is None and (abs(prev_x - x) > 1 or abs(prev_y - y) > 1)):
					print(prev_x,prev_y,"->",x,y)
				
				prev_x = x
				prev_y = y
				
				positions.append((x,y))
			else:
				line = ""
		
		pos_trajectories.append(positions)
	f.close()
	
	temp_trajectories = pos_trajectories
	pos_trajectories = []
	for trajectory in temp_trajectories:
		if(len(trajectory) > 5):
			pos_trajectories.append(trajectory)
	
	full_trajectory = fillTrajectories(pos_trajectories)
	steps = getStepsFromPosTrajectory(full_trajectory)

	test_stepfile = open("zivid_stepfile.txt", "w")
	
	test_stepfile.write(','.join(["(" + str(step[0]) + "," + str(step[1]) + "," + str(step[2]) + ")" for step in steps]))
	
	test_stepfile.close()

if __name__ == "__main__":
	main()
