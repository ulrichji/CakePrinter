import plotter_controller
import random_data_provider

from threading import Thread, Lock, Condition
import random
import time

class BufferedDataProvider(plotter_controller.StepDataProvider):
	# Buffer size is in number of steps
	def __init__(self, data_provider, buffer_size=1024):
		#Setup buffers
		self.read_buffer = []
		self.write_buffer = []
		self.buffer_size = buffer_size
		
		self.data_provider = data_provider
		
		#Threading init
		self.data_loader_thread = Thread(target=self.dataLoaderThread)
		self.swap_condition = Condition()
		
		self.data_loader_thread.daemon = True
		self.data_loader_thread.start()
	
	def swapBuffers(self):
		temp_buffer = self.read_buffer
		self.read_buffer = self.write_buffer
		self.write_buffer = temp_buffer
	
	def requestSwap(self):
		if(len(self.read_buffer) <= 0 and len(self.write_buffer) > 0):
			self.swapBuffers()
			self.swap_condition.notify_all()
	
	def putStep(self):
		self.swap_condition.acquire()
		
		#print("Wait here with ", len(self.write_buffer), self.buffer_size)
		while(len(self.write_buffer) == self.buffer_size):
			#print("Wait for empty")
			self.swap_condition.wait()
			#print("Wake for empty")
		
		step = self.data_provider.getStep()
		
		self.write_buffer.append(step)
		self.requestSwap()
		
		self.swap_condition.release()
	
	def dataLoaderThread(self):
		while(self.data_provider.hasData()):
			self.putStep()
	
	def getStep(self):
		self.swap_condition.acquire()
		
		self.requestSwap()
		
		#print("sizes",len(self.read_buffer), len(self.write_buffer))
		#The two last conditions are strictly speaking not required, but ensures that no strange order has happend emptying the data.
		while(len(self.read_buffer) <= 0 and (len(self.write_buffer) > 0 or self.data_provider.hasData())):
			#print("Wait for fill")
			self.swap_condition.wait()
			#print("Wake for fill")
		
		step = self.read_buffer.pop(0)
		
		if(len(self.read_buffer) == 0):
			self.requestSwap()
		
		self.swap_condition.release()
		return step
	
	def hasData(self):
		self.swap_condition.acquire()
		
		has_data = len(self.read_buffer) > 0 or len(self.write_buffer) > 0 or self.data_provider.hasData()
		
		self.swap_condition.release()
		return has_data

def runTestWithDataProvider(original_provider, buffered_provider, number_of_data, consume_delay=0, consume_delay_width=0):
	do_delay = consume_delay != 0
	random.seed(1235)
	
	for i in range(number_of_data):
		if(not buffered_provider.hasData()):
			raise Exception("Test failed, the provider claimed that data is not accessable")
		
		if(do_delay):
			random_time = (consume_delay_width * random.random()) - consume_delay_width
			sleep_time = max(0, consume_delay + random_time)
		
		step = buffered_provider.getStep()
		correct_step = original_provider.interaction_list.pop(0)
		
		if(step != correct_step):
			raise Exception("Test failed as data is not correct compared to reference")
		
		print("%.2f"%(i * 100.0 / number_of_data), end="\r")
	
	if(buffered_provider.hasData()):
		raise Exception("The data provider claims it has data when it doesn't")
	
def testNodelay(buffer_size, number_of_data=10000):
	original_provider = random_data_provider.RandomDataProvider(number_of_data=number_of_data, seed=123)
	buffered_provider = BufferedDataProvider(original_provider, buffer_size=buffer_size)
	
	runTestWithDataProvider(original_provider, buffered_provider, number_of_data)

def testFasterProvider(buffer_size, number_of_data=10000):
	basic_delay = 0.01
	basic_delay_width = 0.01
	original_provider = random_data_provider.RandomDataProvider(number_of_data=number_of_data, seed=123, delay_time=basic_delay/2, random_delay_variation=basic_delay_width/2)
	buffered_provider = BufferedDataProvider(original_provider, buffer_size=buffer_size)
	
	runTestWithDataProvider(original_provider, buffered_provider, number_of_data, consume_delay=basic_delay, consume_delay_width=basic_delay_width)

def testFasterConsumer(buffer_size, number_of_data=10000):
	basic_delay = 0.01
	basic_delay_width = 0.01
	original_provider = random_data_provider.RandomDataProvider(number_of_data=number_of_data, seed=123, delay_time=basic_delay, random_delay_variation=basic_delay_width)
	buffered_provider = BufferedDataProvider(original_provider, buffer_size=buffer_size)
	
	runTestWithDataProvider(original_provider, buffered_provider, number_of_data, consume_delay=basic_delay/2, consume_delay_width=basic_delay_width/2)

def testEqualTime(buffer_size, number_of_data=10000):
	basic_delay = 0.01
	basic_delay_width = 0.01
	original_provider = random_data_provider.RandomDataProvider(number_of_data=number_of_data, seed=123, delay_time=basic_delay, random_delay_variation=basic_delay_width)
	buffered_provider = BufferedDataProvider(original_provider, buffer_size=buffer_size)
	
	runTestWithDataProvider(original_provider, buffered_provider, number_of_data, consume_delay=basic_delay, consume_delay_width=basic_delay_width)

def run_test():
	for buffer_size in [1, 2, 3, 8, 123, 512, 1001]:
		print("No delay buffer size %d:"%(buffer_size))
		testNodelay(buffer_size)
		print("Faster provider buffer size %d:"%(buffer_size))
		testFasterProvider(buffer_size)
		print("Faster consumer buffer size %d:"%(buffer_size))
		testFasterConsumer(buffer_size)
		print("Equal time buffer size %d:"%(buffer_size))
		testEqualTime(buffer_size)
	
	print("All tests passed!")

if __name__ == "__main__":
	run_test()

