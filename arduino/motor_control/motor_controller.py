import tkinter

import serial
from threading import Thread, Condition
import sys
import glob

class SliderGUIWindow:
	def __init__(self, serial_port):
		self.root = tkinter.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.closeRequested)
		self.slider_value = tkinter.DoubleVar()
		self.scale = tkinter.Scale(self.root, to=1.0, variable=self.slider_value, command=self.valueUpdated, resolution=0)
		self.scale.pack()
		
		self.label = tkinter.Label(self.root)
		self.label.pack()

		self.current_motor_speed = 0
		
		self.serial_thread = Thread(target=self.serialThread)
		self.serial_thread.daemon = True
		self.serial_port = serial_port
		self.running = True
		self.change_condition = Condition()

	def closeRequested(self):
		self.change_condition.acquire()
		self.running = False
		self.change_condition.notify_all()
		self.change_condition.release()
		
		self.serial_thread.join()
		self.root.destroy()
		

	def start(self):
		self.serial_thread.start()
		self.root.mainloop()

	def valueUpdated(self, event):
		self.change_condition.acquire()
		self.current_motor_speed = self.slider_value.get()
		self.change_condition.notify_all()
		self.change_condition.release()

	def serialThread(self):
		ser = serial.Serial(self.serial_port, 9600, timeout=5)
		
		self.change_condition.acquire()
		while(self.running):
			write_byte = bytearray([int(self.current_motor_speed * 255)])
			ser.write(write_byte)
			self.change_condition.wait()
		
		self.change_condition.release()
		ser.write(bytearray([0]))
		ser.close()
		print("I was able to close!")

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

def main():
	if(len(sys.argv) < 2):
		print("Usage: python3 motor_controller.py <serial_port>")
		print("Available ports:")
		print(', '.join(listSerialPorts()))
		return
		
	serial_port = sys.argv[1]
	gui = SliderGUIWindow(serial_port)
	gui.start()

if __name__ == "__main__":
	main()
