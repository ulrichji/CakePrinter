import plotter_controller
import threading
import random
import time
import PIL.Image
import PIL.ImageDraw
import numpy as np
import sys
import step_file_data_provider
import math

class PlotterSimulator:
	def __init__(self, step_time, phys_time, save_image=False, save_stats=True):
		self.image_time_step = 1 / 60
		self.image_size = (600,600)
		self.image_scale = 100
		self.image_center_offset = (0,0)
		self.save_image = save_image
		self.drawn_image = None
		
		self.step_time = step_time
		self.phys_time = phys_time
	
		#some physics constants
		self.x_mass = 1
		self.y_mass = 1
		self.step_size = 0.001
		self.k_x = 600 #The spring stiffness
		self.k_y = 600 #The spring stiffness
		self.c_x = 20
		self.c_y = 20

		self.save_stats = save_stats
		self.stats = {}
		self.clearStats()

		#actual state of the object
		self.state = []
		self.effector_pos = (0,0)
		self.effector_velocity = (0,0)
		self.logical_pos = (0,0)
		
		self.current_time = 0
		self.current_phys_time = 0
		self.step_count = 0
		
		self.current_image_time = 0
		self.image_count = 0

	def getVelocity(self):
		x_vel = self.effector_velocity[0]
		y_vel = self.effector_velocity[1]
		
		return math.sqrt((x_vel**2) + (y_vel**2))

	def clearStats(self):
		self.stats.clear()
		self.stats = {
			'max_force_x_abs':0,
			'max_force_y_abs':0,
			'max_force_x':0,
			'max_force_y':0,
			'min_force_x':0,
			'min_force_y':0,
			'max_velocity_x':0,
			'max_velocity_y':0,
			'min_velocity_x':0,
			'min_velocity_y':0
			}
	
	def getStats(self):
		return self.stats

	def pushState(self):
		this_state = {
			'effector_pos':self.effector_pos,
			'effector_velocity':self.effector_velocity,
			'logical_pos':self.logical_pos,
			'current_time':self.current_time,
			'current_phys_time':self.current_phys_time,
			'step_count':self.step_count,
			'current_image_time':self.current_image_time,
			'image_count':self.image_count
			}
		
		self.state.append(this_state)
	
	def popState(self):
		if(len(self.state) <= 0):
			raise Exception("No state pop.")
		else:
			this_state = self.state.pop()
			self.effector_pos = this_state['effector_pos']
			self.effector_velocity = this_state['effector_velocity']
			self.logical_pos = this_state['logical_pos']
			self.current_time = this_state['current_time']
			self.current_phys_time = this_state['current_phys_time']
			self.step_count = this_state['step_count']
			self.current_image_time = this_state['current_image_time']
			self.image_count = this_state['image_count']
	
	def saveImage(self, draw=False):
		if(self.drawn_image is None):
			self.drawn_image = PIL.Image.new("RGBA", self.image_size)
		while(self.current_phys_time > self.current_image_time and self.save_image):
			
			file_name = "frames/%05d.png"%(self.image_count)
			print("Saving image "+str(file_name))
			
			effector_draw_x = (self.effector_pos[0] * self.image_scale) + self.image_center_offset[0]
			effector_draw_y = (self.effector_pos[1] * self.image_scale) + self.image_center_offset[1]
			logical_draw_x = (self.logical_pos[0] * self.image_scale) + self.image_center_offset[0]
			logical_draw_y = (self.logical_pos[1] * self.image_scale) + self.image_center_offset[1]
			
			if(draw):
				drawer = PIL.ImageDraw.Draw(self.drawn_image)
				drawer.point((effector_draw_x, effector_draw_y), fill=(255, 255, 255, 255))
				del drawer
			
			img = self.drawn_image.copy()
			drawer = PIL.ImageDraw.Draw(img)
			
			drawer.line([effector_draw_x, effector_draw_y, effector_draw_x, effector_draw_y], fill=(255,0,0,255))
			drawer.line([logical_draw_x, logical_draw_y, logical_draw_x, logical_draw_y], fill=(0,0,255,255))
			drawer.line([effector_draw_x, effector_draw_y, logical_draw_x, logical_draw_y], fill=(0,255,0,255))
			drawer.text((0,0),"%.5f"%(self.current_image_time), fill=(255,255,255,255))
			del drawer
			
			img.save(file_name, "PNG")
			
			self.current_image_time += self.image_time_step
			self.image_count += 1
	
	def stepPhysics(self, draw=False):
		while(self.current_phys_time < self.current_time):
			offset_x = self.logical_pos[0] - self.effector_pos[0]
			offset_y = self.logical_pos[1] - self.effector_pos[1]
			
			#This is actually two separate system as the actuators for the plotter is an x-y system.
			force_x = (offset_x * self.k_x) - (self.c_x * self.effector_velocity[0])
			force_y = (offset_y * self.k_y) - (self.c_y * self.effector_velocity[1])
			
			acceleration_x = force_x / self.x_mass # Don't include time as it's not a motion formula
			acceleration_y = force_y / self.y_mass # Don't include time as it's not a motion formula
			
			velocity_x = self.effector_velocity[0] + (acceleration_x * self.phys_time) #Include time as it's a motion formula
			velocity_y = self.effector_velocity[1] + (acceleration_y * self.phys_time) #Include time as it's a motion formula
			
			movement_x = self.effector_pos[0] + (velocity_x * self.phys_time)
			movement_y = self.effector_pos[1] + (velocity_y * self.phys_time)
			
			self.effector_velocity = (velocity_x, velocity_y)
			self.effector_pos = (movement_x, movement_y)
			self.saveImage(draw)
			
			if(self.save_stats):
				self.stats['max_force_x_abs'] = max(abs(force_x), self.stats['max_force_x_abs'])
				self.stats['max_force_y_abs'] = max(abs(force_y), self.stats['max_force_y_abs'])
				self.stats['max_force_x'] = max(force_x, self.stats['max_force_x'])
				self.stats['max_force_y'] = max(force_y, self.stats['max_force_y'])
				self.stats['min_force_x'] = min(force_x, self.stats['min_force_x'])
				self.stats['min_force_y'] = min(force_y, self.stats['min_force_y'])
			
			self.current_phys_time += self.phys_time
	
	def step(self, step):
		x_diff = 0
		y_diff = 0
		if(step.x_step == plotter_controller.StepDirection.FORWARD):
			x_diff += 1
		elif(step.x_step == plotter_controller.StepDirection.BACKWARDS):
			x_diff -= 1
		if(step.y_step == plotter_controller.StepDirection.FORWARD):
			y_diff += 1
		elif(step.y_step == plotter_controller.StepDirection.BACKWARDS):
			y_diff -= 1
		
		new_pos_x = self.logical_pos[0] + (x_diff * self.step_size)
		new_pos_y = self.logical_pos[1] + (y_diff * self.step_size)
		self.logical_pos = (new_pos_x, new_pos_y)
		
		self.current_time += self.step_time
		self.stepPhysics(draw=step.draw_value > 0)
		
		self.step_count += 1

class PlotterSimulatorController(plotter_controller.PlotterController):
	def __init__(self, step_data, step_time=0.001, buffer_size=1024, save_images=False):
		super(PlotterSimulatorController, self).__init__(step_data, step_time)
		
		self.effector_pos = (0,0)
		self.stepper_thread = None
		self.data_thread = None
		self.simulator = PlotterSimulator(step_time, step_time / 10, save_image=save_images)
		
		self.buffer_size = buffer_size
		self.load_buffer = []
		self.consume_buffer = []
		self.buffers = []
		self.has_data = True
	
	def wait(self):
		self.stepper_thread.join()
		self.data_thread.join()
	
	#Buffer size should be large enough to handle latencies in the system.
	def stepThreadFunc(self):
		while(self.has_data):
			#wait for data
			#print(self.has_data, self.consume_buffer, self.load_buffer)
			while(self.has_data and len(self.consume_buffer) <= 0):
				time.sleep(0)
			#print(self.consume_buffer, self.load_buffer)
			
			start_time = time.time()
			step_index = 0
			while(len(self.consume_buffer) > 0):
				step = self.consume_buffer.pop(0)
				self.simulator.step(step)
				step_index += 1
				
				current_time = time.time()
				next_step_time = start_time + ((step_index)*self.step_time)
				sleep_time = max(next_step_time - current_time, 0)
				time.sleep(sleep_time)
			
	
	def dataThreadFunc(self):
		while(self.step_data.hasData()):
			step = self.step_data.getStep()
			self.load_buffer.append(step)
			
			if(len(self.load_buffer) >= self.buffer_size or not self.step_data.hasData()):
				#Wait for consume buffer to empty
				while(len(self.consume_buffer) > 0):
					time.sleep(0)
				#And now swap the buffers
				temp_buffer = self.load_buffer
				self.load_buffer = self.consume_buffer
				self.consume_buffer = temp_buffer
				time.sleep(0)
		
		self.has_data = False
	
	def start(self):
		self.stepper_thread = threading.Thread(target=self.stepThreadFunc)
		self.data_thread = threading.Thread(target=self.dataThreadFunc)
		self.stepper_thread.start()
		self.data_thread.start()

class RandomDataProvider(plotter_controller.StepDataProvider):
	def __init__(self, number_of_data=1):
		self.data_left = number_of_data
	
	def getStep(self):
		if(self.data_left <= 0):
			raise Exception("Program crashed as the data provider is out of data")
		else:
			x_step = random.choice(list(plotter_controller.StepDirection))
			y_step = random.choice(list(plotter_controller.StepDirection))
			self.data_left -= 1
			return plotter_controller.PlotterStep(x_step, y_step)
	
	def hasData(self):
		return self.data_left > 0

def main():
	data_provider = None
	if(len(sys.argv) > 1):
		data_provider = step_file_data_provider.StepFileDataProvider(sys.argv[1])
	else:
		data_provider = RandomDataProvider(number_of_data=10000)
	
	controller = PlotterSimulatorController(data_provider, save_images=True)
	controller.start()
	
	controller.wait()

if __name__ == "__main__":
	main()
