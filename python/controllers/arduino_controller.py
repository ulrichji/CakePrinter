import plotter_controller
import buffered_data_provider
import step_file_data_provider
import joining_data_provider

import argparse

import sys
import glob
import serial

def listSerialPorts():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        ports = []

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def linearizePump(pump_val):
	if(pump_val > 0):
		return (pump_val * 0.25) + 0.25
	else:
		return 0

def convertStepsToBinary(steps_list):
	bytes = []
	
	prev_x_dir = 0
	prev_y_dir = 0
	
	for step in steps_list:
		x_dir_bit = 1 if step.x_step == plotter_controller.StepDirection.FORWARD else 0
		x_step_bit = 1 if step.x_step != plotter_controller.StepDirection.NONE else 0
		y_dir_bit = 0 if step.y_step == plotter_controller.StepDirection.FORWARD else 1
		y_step_bit = 1 if step.y_step != plotter_controller.StepDirection.NONE else 0
		
		pump_val = linearizePump(step.draw_value)
		pump_velocity = int(pump_val * 255)
		
		byteval = 0
		byteval |= (pump_velocity & 0xF0)
		byteval |= (x_dir_bit << 3)
		byteval |= (x_step_bit << 2)
		byteval |= (y_dir_bit << 1)
		byteval |= (y_step_bit << 0)
		
		byteval &= 0xFF
		
		bytes.append(byteval)
	
	bytes = bytearray(bytes)
	return bytes

class ArduinoController:
	def __init__(self, data_provider, serial_port, baud_rate=57600):
		self.data_provider = data_provider
		self.serial_port = serial_port
		self.baud_rate = baud_rate
		self.send_buffer = []
		self.send_buffer_size = 512

	def fillData(self):
		step_buffer = []
		while(len(step_buffer) < self.send_buffer_size and self.data_provider.hasData()):
			step_buffer.append(self.data_provider.getStep())
		
		self.send_buffer = convertStepsToBinary(step_buffer)

	def start(self):
		print("Connecting to "+str(self.serial_port) + ", baud rate: "+str(self.baud_rate))
		ser = serial.Serial(self.serial_port, self.baud_rate, timeout=5)
		
		self.fillData()
		
		data_count = 0
		
		while(len(self.send_buffer) > 0):
			line = ser.readline().decode('ascii').strip()
			print("Got command \""+str(line)+"\"")
			
			if(line == "Ready"):
				print("Sending bytes %d to %d"%(data_count, data_count + len(self.send_buffer)))
				ser.write(self.send_buffer)
				
				data_count += len(self.send_buffer)
				self.send_buffer.clear()
				self.fillData()
		
		print("Closing transmission")
		ser.close()
		
		print("Done")

def runArduinoFileSteps(serial_port, file_list):
	joined_provider = joining_data_provider.JoiningDataProvider()
	for file_path in file_list:
		file_provider = step_file_data_provider.StepFileDataProvider(file_path)
		joined_provider.addDataProvider(file_provider)
	
	#As the underlying providers are file based, create a buffered data provider to avoid unstable performance
	buffered_provider = buffered_data_provider.BufferedDataProvider(joined_provider)
	
	controller = ArduinoController(buffered_provider, serial_port)
	controller.start()

def main():
	serial_port = None
	file_list = []

	parser = argparse.ArgumentParser(description='Control a plotter from a step file')
	parser.add_argument('--serial_port', type=str, nargs='?', help="The serial port to use.")
	parser.add_argument('--files', type=str, nargs='+', help="A list of files to send to the plotter")
	
	args = parser.parse_args()
	if(args.serial_port is None):
		print("Serial port is a required argument!")
		print("Looking for available ports...")
		serial_ports = listSerialPorts()
		for port in serial_ports:
			print("Port: "+str(port))
		if(len(serial_ports) == 0):
			print("Found no available serial ports")
		return
	
	serial_port = args.serial_port
	file_list.extend(args.files)
	
	runArduinoFileSteps(serial_port, file_list)
	
if __name__ == "__main__":
	main()
