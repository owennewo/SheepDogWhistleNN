#include "pins.h"

#include <SimpleFOC.h>
// #include <Wire.h>
// #include "imu_helpers.h"
#include <VescRemote.h>


BLDCMotor motorLeft = BLDCMotor(7);
BLDCDriver3PWM driverLeft = BLDCDriver3PWM(M0_A, M0_B, M0_C);

BLDCMotor motorRight = BLDCMotor(7);
BLDCDriver3PWM driverRight = BLDCDriver3PWM(M1_A, M1_B, M1_C);


// MagneticSensorI2C sensorLeft = MagneticSensorI2C(AS5600_I2C);
// MagneticSensorI2C sensorRight = MagneticSensorI2C(AS5600_I2C);

VescRemote remote;

// #define LEFT_FORWARD  RC2_0
// #define LEFT_BACK     RC2_1
// #define RIGHT_FORWARD RC2_2
// #define RIGHT_BACK    RC2_3


// #define LEFT_FORWARD  POT1
// #define LEFT_BACK     POT2
// #define RIGHT_FORWARD RC2_2
// #define RIGHT_BACK    POT0

#define MAX_SPEED 3

float Right = 0;
float Left = 0;
float steer = 0;
float speed = 0;



HardwareSerial Serial1(USART1_RX, USART1_TX);
HardwareSerial Serial3(USART3_RX, USART3_TX);

#define Serial Serial3

TwoWire Wire2(I2C1_SDA, I2C1_SCL);

// HardwareSerial serial1(USART1_RX, USART1_TX);

Commander command = Commander(Serial);
void doRight(char* cmd) { 
  Serial.println("right");
  Left = 1.0;
  Right = -1.0;
}

void doLeft(char* cmd) { 
  Serial.println("left");
  Left = -1.0;
  Right = 1.0;
  // Serial.println(Left); 
}

void doGo(char* cmd) { 
  Serial.println("go");
  Left = 1.0;
  Right = 1.0;
  // Serial.println(Left); 
}

void doStop(char* cmd) { 
  Serial.println("stop");
  Left = 0.0;
  Right = 0.0;
   
}

void setup() {

  Serial.begin(115200);

  delay(1000);
  Serial.println("setup");

  pinMode(USART1_RX, INPUT);

  Serial.println("setup2");

  analogWriteFrequency(25000);

  remote.begin(Serial1);
  
  pinMode(PB12, OUTPUT);
  
  digitalWrite(PB12, HIGH);
  delay(50);
  digitalWrite(PB12, LOW);
  delay(50);
  digitalWrite(PB12, HIGH);
  delay(200);
  Serial.println("setup3");

  driverLeft.voltage_power_supply = 12;
  driverLeft.init();
  Serial.println("setup3a");
  driverRight.voltage_power_supply = 12;
  driverRight.init();
  
  Serial.println("setup3b");

  digitalWrite(PB12, HIGH);
  delay(50);
  digitalWrite(PB12, LOW);
  delay(50);
  digitalWrite(PB12, HIGH);
  delay(200);

  // link the motorLeft and the driverLeft
  motorLeft.linkDriver(&driverLeft);
  motorLeft.voltage_limit = 2.0;   // [V]
  motorLeft.velocity_limit = 5;
  motorLeft.useMonitoring(Serial);

  motorLeft.controller = MotionControlType::velocity_openloop;

  motorRight.linkDriver(&driverRight);
  motorRight.voltage_limit = 2.5;   // [V]
  motorRight.voltage_sensor_align = 4.0;   // [V]
  motorRight.velocity_limit = 5;
  motorRight.useMonitoring(Serial);

  motorRight.controller = MotionControlType::velocity_openloop;
  motorRight.velocity_limit;
  motorRight.PID_velocity.limit;

  // // init motorLeft hardware
  motorLeft.sensor_offset = -2;
  motorLeft.init();
  motorLeft.initFOC(0.01, CCW);

  motorRight.sensor_offset = 1.5;
  motorRight.init();
  motorRight.initFOC(0.01, CW);
  // Serial.println(motorRight.zero_electric_angle);


  Serial.print("zero: ");
  Serial.println(motorRight.zero_electric_angle);

  delay(2000);

  // // add target command T
  command.add('l', doLeft, "left");
  command.add('r', doRight, "right");
  command.add('s', doStop, "stop");
  command.add('g', doGo, "go");

}

void loop() {

//  Serial.print("."); 
  

 motorLeft.move(MAX_SPEED * Left);
 motorLeft.loopFOC();
 
 motorRight.move(MAX_SPEED * Right);
 motorRight.loopFOC();
 
 command.run();

  static long last = 0;
  long now = millis();

  if (remote.readData()) {
    // Serial.println("read");
        // Serial.println(remote.data.x1);
        // Left = remote.data.x1;
        // Right = -remote.data.y1;
        steer = remote.data.x2;
        speed = remote.data.y2;

        Left =  (speed + steer);
        Right = (speed - steer);



        // int right_forward = right >= 0 ? min(255, int(right * 255)): 0;
        // int left_forward = left >= 0 ? min(255, int(left * 255)): 0;
        // int right_back = right < 0 ? min(255, int(-right * 255)): 0;
        // int left_back = left < 0 ? min(255, int(-left * 255)): 0;

        // Serial.print(right_forward); Serial.print("\t");
        // Serial.print(left_forward); Serial.print("\t");
        Serial.print(Left); Serial.print("\t");
        Serial.println(Right);

        //  delay(100);
        // digitalWrite(PB12, LOW);
        // analogWrite(RIGHT_FORWARD, right_forward);
        // analogWrite(LEFT_FORWARD, left_forward);

        // analogWrite(RIGHT_BACK, right_back);
        // analogWrite(LEFT_BACK, left_back);


  }

  if (now - last > 200) {
    Serial.print(".");
    // Serial.print(sensorLeft.getAngle());
    // Serial.print("\t");
    // Serial.print(sensorLeft.getVelocity());
    // Serial.print("\t");
    // Serial.print(motorLeft.shaft_angle);
    // Serial.print("\t");
    // Serial.print(motorLeft.shaft_velocity);
    // Serial.print("\t");  
    // Serial.print(motorRight.shaft_angle);
    // Serial.print("\t");
    // Serial.println(motorRight.shaft_angle);
    last = now;
  }

  
}