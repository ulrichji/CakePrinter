import plotter_controller

class JoiningDataProvider(plotter_controller.StepDataProvider):
	def __init__(self):
		self.providers_list = []
		self.current_provider = None
	
	def updateCurrentProvider(self):
		if(self.current_provider is None and len(self.providers_list) > 0):
			self.current_provider = self.providers_list.pop(0)
		
		while((not self.current_provider is None) and (not self.current_provider.hasData())):
			if(len(self.providers_list) <= 0):
				self.current_provider = None
			else:
				self.current_provider = self.providers_list.pop(0)
	
	def addDataProvider(self, data_provider):
		self.providers_list.append(data_provider)
		self.updateCurrentProvider()
	
	def getStep(self):
		step = self.current_provider.getStep()
		self.updateCurrentProvider()
		return step
	
	def hasData(self):
		return (not self.current_provider is None) and self.current_provider.hasData()
