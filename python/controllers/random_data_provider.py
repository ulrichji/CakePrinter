import plotter_controller
import random
import time

class RandomDataProvider(plotter_controller.StepDataProvider):
	def __init__(self, number_of_data=0, delay_time=0, random_delay_variation=0, seed=None):
		if(not seed is None):
			random.seed(seed) # Start the psuedo-rng to get deterministic behaviour of tests
		
		self.infinite_data = number_of_data == 0
		self.n_data_left = number_of_data
		# Sleep(0) is basically a yield function, which is not typical for no-delay providers
		self.do_sleep = delay_time != 0
		
		self.delay_time = delay_time
		self.random_delay_variation = random_delay_variation
		
		self.data_count = 0
		self.last_step = None
		self.interaction_list = []

	def delayData(self):
		if(self.do_sleep):
			random_delay = max(0, (random.random() * self.random_delay_variation) - (0.5 * self.random_delay_variation))
			sleep_time = max(0, self.delay_time + random_delay)
			time.sleep(sleep_time)

	def getStep(self):
		x_dir = random.choice(list(plotter_controller.StepDirection))
		y_dir = random.choice(list(plotter_controller.StepDirection))
		draw_value = 1
		
		self.delayData()
		
		if(self.n_data_left <= 0):
			return None
		
		self.data_count += 1
		self.n_data_left -= 1
		self.last_step = plotter_controller.PlotterStep(x_dir, y_dir, draw_value=draw_value)
		self.interaction_list.append(self.last_step)
		
		return self.last_step

	def hasData(self):
		return self.n_data_left > 0 or self.infinite_data
