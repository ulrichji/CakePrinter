
#include <TimerOne.h>
#include "MeOrion.h"

#define BUFFER_SIZE 512

int stepper1Dir = 11;   //PB3
int stepper1Step = 10;  //PB2
int stepper2Dir = 3;    //PD3
int stepper2Step = 9;   //PB1

//Allocate space for two buffers
uint8_t firstBuffer [BUFFER_SIZE];
uint8_t secondBuffer [BUFFER_SIZE];

//Double buffering is used, such that these are swapped when needed
uint8_t* readBuffer;
uint8_t* writeBuffer;

//What byte in the read buffer we are reading
int readPos = 0;
//Boolean value used to determine if the write buffer is ready to write into
bool writeEmpty = 1;

uint8_t lastPumpVel = 0;
MeDCMotor pump(M1);

void setup()
{
  Serial.begin(57600);

  pinMode(stepper1Dir,OUTPUT);
  pinMode(stepper1Step,OUTPUT);
  pinMode(stepper2Dir,OUTPUT);
  pinMode(stepper2Step,OUTPUT);

  //This is a timer used to interrupt to do the step function of the stepper motors.
  Timer1.initialize(200);
  Timer1.attachInterrupt(stepTime);
}

//Function will swap write and read buffers. Swap buffers if the other buffer is not full
//Returns 0 if the buffers were swapped and 1 if the write buffer is not ready.
bool swapBuffers()
{
  //make sure that the other buffer is full
  if(writeEmpty == 0)
  {
    //swap the buffers
    uint8_t* tempBuffer = readBuffer;
    readBuffer = writeBuffer;
    writeBuffer = readBuffer;

    //Set the write buffer to ready to be filled.
    writeEmpty = 1;
    //Set read position to beginning of 
    readPos = 0;
    return 0; //return success
  }

  //The write buffer is not full. Reutrn not successfull
  return 1;
}

int phase = 0;

//Step the steppers
void stepTime()
{
  uint8_t nextStepData = readBuffer[readPos];

  uint8_t stepBit1 = (nextStepData & 0x4) >> 2;
  uint8_t dirBit1  = (nextStepData & 0x8) >> 3;
  uint8_t stepBit2 = (nextStepData & 0x1) >> 0;
  uint8_t dirBit2  = (nextStepData & 0x2) >> 1;

  if(phase == 0)
  {
    if(readPos < BUFFER_SIZE)
    {
      readPos++;
    }
    //The buffer is consumed. Try to swap buffers
    else
    {
      if(swapBuffers())
      {
        return;
      }
    }
    
    //Set direction
    PORTB ^= (-dirBit1  ^ PORTB) & (1 << PB3);
    PORTD ^= (-dirBit2  ^ PORTD) & (1 << PD3);

    //Do the stepping
    PORTB ^= (-stepBit1 ^ PORTB) & (1 << PB2);
    PORTB ^= (-stepBit2 ^ PORTB) & (1 << PB1);
    
    uint8_t pumpVel = nextStepData & 0xF0;
    if(pumpVel != lastPumpVel)
    {
      pump.run(pumpVel);
      lastPumpVel = pumpVel;
    }
    phase = 1;
  }
  else
  {
    //Clear step
    PORTB &= (1 << PB2);
    PORTB &= (1 << PB1);
    
    phase = 0;
  }
  
  //The data from serial directly sets the values of the dir and step pins
  //The table shows the connections of the data sent from serial
  //bit    |     3    |     2     |     1    |     0     |
  //       |step 1 dir|step 1 step|step 2 dir|step 2 step|
  //uint8_t step1Data = nextStepData & 0xC;
  //uint8_t step2Data = nextStepData & 0x3;

  //uint8_t stepBit1 = (nextStepData & 0x4) >> 2;
  //uint8_t dirBit1  = (nextStepData & 0x8) >> 3;
  //uint8_t stepBit2 = (nextStepData & 0x1) >> 0;
  //uint8_t dirBit2  = (nextStepData & 0x2) >> 1;
  
  //uint8_t step_b_set = (stepBit1 << PB2) || (stepBit2 << PB1);
  //uint8_t step_b_clear = ~((1 << PB2) | (1 << PB1));

  //Set directional bits
  //PORTB ^= (-dirBit1  ^ PORTB) & (1 << PB3);
  //PORTD ^= (-dirBit2  ^ PORTD) & (1 << PD3);
 
  //PORTB &= step_b_clear;
  //PORTB |= step_b_set;

  //This goes first because it should set direction before step
  //PORTD |= (dirBit2 << PD3);
  //PORTB |= (stepBit1 << PB2) | (0 << PB3) | (stepBit2 << PB1);
  
  //PORTB ^= (-stepBit1 ^ PORTB) & (1 << PB2);
  //PORTB ^= (-dirBit1  ^ PORTB) & (1 << PB3);
  //PORTB ^= (-stepBit2 ^ PORTB) & (1 << PB1);
  //PORTD ^= (-dirBit2  ^ PORTD) & (1 << PD3);
}

void loop()
{
  //setup start values for the buffers
  readPos = BUFFER_SIZE;
  readBuffer = firstBuffer;
  writeBuffer = secondBuffer;
  writeEmpty = 1; //Make sure that the write buffer is ready to be filled
  
  while(1)
  {
    delay(0.02);
    //If the write buffer is emptied, it should be filled up from serial.
    if(writeEmpty == 1)
    {
      Serial.println("Ready");
      int nbytes = Serial.readBytes(writeBuffer, BUFFER_SIZE);
      if(nbytes != 0)
        writeEmpty = 0;
    }
  }
}
