/**
 * \par Copyright (C), 2012-2015, MakeBlock
 * @file    DCMotorDriverTest.ino
 * @author  MakeBlock
 * @version V1.0.0
 * @date    2015/09/09
 * @brief   Description: this file is sample code for Me DC motor device.
 *
 * Function List:
 *    1. void MeDCMotor::run(int16_t speed)
 *    2. void MeDCMotor::stop(void)
 *
 * \par History:
 * <pre>
 * <Author>     <Time>        <Version>      <Descr>
 * Mark Yan     2015/09/09    1.0.0          rebuild the old lib
 * </pre>
 */
#include "MeOrion.h"

MeDCMotor pump(M1);

uint8_t motor_speed = 255;

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  while(1)
  {
    pump.run(motor_speed);
  }
}

