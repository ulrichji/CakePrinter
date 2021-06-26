import plotter_controller
import plotter_simulator
import step_file_data_provider

class SmoothedStepDataProvider(plotter_controller.StepDataProvider):
	def __init__(self, data_provider):
		self.data_provider = data_provider
		self.step_buffer = []
		self.data_taken = False
		self.simulator = plotter_simulator.PlotterSimulator(0.001, 0.0001)
		self.current_data = 0
	
	def fillBuffer(self, size):
		if(len(self.step_buffer) < size):
			size_diff = size - len(self.step_buffer)
			while(size_diff > 0 and self.data_provider.hasData()):
				self.step_buffer.append(self.data_provider.getStep())
				size_diff -= 1
			
			if(not self.data_provider.hasData()):
				self.data_taken = True
	
	def getStep(self):
		# Want to simulate at least one
		self.fillBuffer(1)
		step = self.step_buffer[0]
		step_changed = False
		
		self.simulator.pushState()
		self.simulator.clearStats()
		self.simulator.step(step)
		stats = self.simulator.getStats()
		self.simulator.popState()
		pump_velocity = min(step.draw_value, self.simulator.getVelocity() / 1.0)
		if(step.x_step == plotter_controller.StepDirection.FORWARD and (stats['max_force_x'] > 1.0 or stats['max_velocity_x'] > 1.0)):
			step_changed = True
			step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
		elif(step.x_step == plotter_controller.StepDirection.BACKWARDS and (stats['min_force_x'] < -1.0 or stats['min_velocity_x'] < -1.0)):
			step_changed = True
			step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
		elif(step.y_step == plotter_controller.StepDirection.FORWARD and (stats['max_force_y'] > 1.0 or stats['max_velocity_x'] > 1.0)):
			step_changed = True
			step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
		elif(step.y_step == plotter_controller.StepDirection.BACKWARDS and (stats['min_force_y'] < -1.0 or stats['min_velocity_x'] < -1.0)):
			step_changed = True
			step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
		
		#Now compare constraint breaking in the opposite direction
		if(not step_changed):
			velocity = self.simulator.effector_velocity
			x_sim_time = self.simulator.x_mass * abs(velocity[0]) / 1.0
			y_sim_time = self.simulator.y_mass * abs(velocity[1]) / 1.0
			sim_time = max(x_sim_time, y_sim_time)
			
			number_of_steps = int((0.5 * sim_time) / self.simulator.step_time)
			self.fillBuffer(number_of_steps)
			
			#Now do the simulation
			self.simulator.pushState()
			self.simulator.clearStats()
			
			for i in range(min(len(self.step_buffer), number_of_steps)):
				inloop_step = self.step_buffer[i]
				self.simulator.step(inloop_step)
			#If unable to fill buffer, add more.
			for i in range(max(number_of_steps - len(self.step_buffer), 0)):
				self.simulator.step(plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity))
			
			stats = self.simulator.getStats()
			self.simulator.popState()
			
			if(step.x_step == plotter_controller.StepDirection.FORWARD and stats['min_force_x'] < -1.0):
				step_changed = True
				step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
			elif(step.x_step == plotter_controller.StepDirection.BACKWARDS and stats['max_force_x'] > 1.0):
				step_changed = True
				step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
			elif(step.y_step == plotter_controller.StepDirection.FORWARD and stats['min_force_y'] < -1.0):
				step_changed = True
				step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
			elif(step.y_step == plotter_controller.StepDirection.BACKWARDS and stats['max_force_y'] > 1.0):
				step_changed = True
				step = plotter_controller.PlotterStep(plotter_controller.StepDirection.NONE, plotter_controller.StepDirection.NONE, pump_velocity)
		
		self.simulator.clearStats()
		self.simulator.step(step)
		print("%.6f"%(self.simulator.current_phys_time), self.current_data, end="\r")
		#print("%.5f"%(self.simulator.current_phys_time), self.current_data, step, self.simulator.getStats()['max_force_x_abs'], self.simulator.getStats()['max_force_y_abs'])
		if(not step_changed):
			self.step_buffer.pop(0)
			self.current_data += 1
		
		return step
	
	def hasData(self):
		return (not self.data_taken) or (len(self.step_buffer) > 0)

def stepToText(step):
	x_text = '0'
	y_text = '0'
	draw_text = str(step.draw_value)
	if(step.x_step == plotter_controller.StepDirection.FORWARD):
		x_text = '1'
	elif(step.x_step == plotter_controller.StepDirection.BACKWARDS):
		x_text = '-1'
	if(step.y_step == plotter_controller.StepDirection.FORWARD):
		y_text = '1'
	elif(step.y_step == plotter_controller.StepDirection.BACKWARDS):
		y_text = '-1'
	
	return '(' + str(x_text) + ',' + str(y_text) + ',' + str(draw_text) + ')'

def main():
	smoothed_step_file = open("zivid_stepfile_smooth.txt", "w")
	file_data_provider = step_file_data_provider.StepFileDataProvider("zivid_stepfile.txt")
	smoothed_data_provider = SmoothedStepDataProvider(file_data_provider)
	while(smoothed_data_provider.hasData()):
		step = smoothed_data_provider.getStep()
		smoothed_step_file.write(stepToText(step))
		if(smoothed_data_provider.hasData()):
			smoothed_step_file.write(',')
	
	
if __name__ == "__main__":
	main()
