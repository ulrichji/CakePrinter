# Plotter controller
This project is the plotter controller written using the Arduino framework.
The project use some low-level AVR-instructions.
This is because it is concerned with performance restricions and requires a short step time for a smooth movement.


## Requirements
These are the libraries required to compile this project.
- 	Requires the MeOrion.h library <https://github.com/Makeblock-official/Makeblock-Libraries/>. 
	Installation instructions are found on that website.
-	Timer1 from <https://playground.arduino.cc/code/timer1>.
	Installation instructions are found on that website (it's quite simple)

## Interface
This section will describe the interface used by the controller, eg. how to use it.
The arduino will be reffered to as the "device" and the computer connected to it will be reffered to as "server". 

### Overall communication
The arduino is the unit that will controll the dataflow.
At startup, the device starts a serial communication with a baud rate of 57600. 
This baud rate must be matched by server. 
Every time the device is ready to receive data, it will send "Ready\n" on the serial interface.
Now the server can send data, but doesn't have to and can wait for the next "Ready" message.
The server message is a 512 bytearray representing the steps. Format is explained in next section.
The server will wait for the next "Ready" message before it sends the next 512 bytes etc.

### Data format
The message is 512 bytes each represning the next 512 steps the plotter should perform.
Each byte represents a step using the following convention.

- [7 - 4] The pump velocity. This is a 4-bit number.
- [3] Step direction in x. 0 is backwards and 1 is forwards.
- [2] Step in x. 0 means no step in x-direction and 1 means to step in the direction indicated by bit 3
- [1] Step direction y. 0 is backwards and 1 is forwards.
- [0] Step in y. 0 means no step in y-direction and 1 means to step in the direction indicated by bit 1.

## System
This section will describe how the system is designed.

The system is based on a very simple arduino client which itself controls when it will have data.
It will immediately begin consuming the data when it has received it.
It is implemented as a double buffered system.
The TimerOne library is used to control the steps. 
It creates an interrupt that enables multiprogramming such that it can receive bytes in one buffer while it consumes bytes in the other.
The step is itself is based on low level AVR-memory handling to maximize per-step performance.
The motor controller is controlled using the MeDCMotor class from the MeOrion library.

