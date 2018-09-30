from enum import Enum

class StepDirection(Enum):
	NONE = 0
	FORWARD = 1
	BACKWARDS = 2

class PlotterStep:
	def __init__(self, x_step, y_step):
		self.x_step = x_step
		self.y_step = y_step
	
	def __str__(self):
		return "Step: " + str(self.x_step) + ", " + str(self.y_step)

	def __eq__(self, other):
		return self.x_step == other.x_step and self.y_step == other.y_step

class PlotterController:
	#default initialization with a data provider and a step_time
	def __init__(self, step_data, step_time=0.001):
		self.step_data = step_data
		self.step_time = step_time
	
	def start(self):
		raise Exception("The plotter controller must be inherited in order to start")
	
	

class StepDataProvider:
	def getStep(self):
		raise Exception("Step data must be inherited for some type of data.")
	
	def hasData(self):
		raise Exception("This must be inherited")
