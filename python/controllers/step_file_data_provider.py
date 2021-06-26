import plotter_controller

class StepFileDataProvider(plotter_controller.StepDataProvider):
	def __init__(self, file_path, buffer_size=1024):
		self.file_path = file_path
		self.has_data = True
		self.step_file = None
		self.number_of_steps = 0
		
		self.buffer_size = buffer_size
		self.buffer = ""
		
		self.at_end = False
		self.next_step = None
	
	def textStepToStepData(self, step_text):
		int_val = int(step_text)
		if(int_val < 0):
			return plotter_controller.StepDirection.BACKWARDS
		elif(int_val > 0):
			return plotter_controller.StepDirection.FORWARD
		else:
			return plotter_controller.StepDirection.NONE
	
	def textStepToDrawValue(self, text_step):
		return float(text_step)
	
	def openFile(self):
		self.step_file = open(self.file_path, "r")
	
	def closeFile(self):
		self.step_file.close()
	
	def parseNextStep(self):
		step_start = self.buffer.find('(')
		step_end = self.buffer.find(')')
		
		if(step_start >= 0 and step_end >= 0):
			step_text = self.buffer[step_start+1:step_end]
			step_split = step_text.split(',')
			x_step = self.textStepToStepData(step_split[0])
			y_step = self.textStepToStepData(step_split[1])
			draw_value = 0
			if(len(step_split) > 2):
				draw_value = self.textStepToDrawValue(step_split[2])
			
			self.buffer = self.buffer[step_end+1:]
			
			return plotter_controller.PlotterStep(x_step, y_step, draw_value=draw_value)
		else:
			return None
	
	def parseStep(self):
		step = self.parseNextStep()
		while(step is None and self.at_end == False):
			pre_buffer_size = len(self.buffer)
			self.buffer += self.step_file.read(self.buffer_size)
			post_buffer_size = len(self.buffer)
			
			if(post_buffer_size > pre_buffer_size):
				step = self.parseNextStep()
			else:
				self.at_end = True
		
		return step
	
	def initFile(self):
		self.openFile()
		self.next_step = self.parseStep()
		if(self.next_step is None):
			self.has_data = False
		else:
			self.has_data = True
	
	def getStep(self):
		if(self.step_file is None):
			self.initFile()
		
		return_data = self.next_step
		self.next_step = self.parseStep()
		
		if(self.next_step is None):
			self.has_data = False
		
		self.number_of_steps += 1
		return return_data
	
	def hasData(self):
		if(self.step_file is None):
			self.initFile()
		return self.has_data
	
	def getStepOld(self):		
		while(self.has_data):
			buffer += f.read(buffer_size)
			at_end = len(buffer) < buffer_size
			
			found_step = True
			while(found_step):
				step_start = buffer.find('(')
				step_end = buffer.find(')')
				if(step_start >= 0 and step_end >= 0):
					step_text = buffer[step_start+1:step_end]
					step_split = step_text.split(',')
					
					print("Found step " + step_text)
					
					x_step = self.textStepToStepData(step_split[0])
					y_step = self.textStepToStepData(step_split[1])
					
					buffer = buffer[step_end+1:]
					
					yield plotter_controller.PlotterStep(x_step, y_step)
				else:
					found_step = False
			
			if(at_end):
				self.has_data = False

def main():
	file_path = "stepfile.txt"
	data_provider = StepFileDataProvider(file_path)
	cnt = 0
	while(data_provider.hasData()):
		print((cnt+1), data_provider.getStep())
		cnt += 1
	
	print("Done after %d steps"%(cnt))

if __name__ == "__main__":
	main()
