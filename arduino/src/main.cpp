#include "pins.h"

#include <SimpleFOC.h>
// #include <VescRemote.h>

LowPassFilter lpf_left{.Tf = 0.25};;
LowPassFilter lpf_right{.Tf = 0.25};;

BLDCMotor motorLeft = BLDCMotor(7);
BLDCDriver3PWM driverLeft = BLDCDriver3PWM(M0_A, M0_B, M0_C);

BLDCMotor motorRight = BLDCMotor(7);
BLDCDriver3PWM driverRight = BLDCDriver3PWM(M1_A, M1_B, M1_C);

// VescRemote remote;

#define MAX_SPEED 6
#define VOLTAGE_LIMIT 5.0
#define LED_PIN PB12

float Right = 0;
float Left = 0;

float steer = 0;
float speed = 0;

HardwareSerial Serial1(USART1_RX, USART1_TX);
HardwareSerial Serial3(USART3_RX, USART3_TX);

#define Serial Serial3

TwoWire Wire2(I2C1_SDA, I2C1_SCL);

void motorsOff() {
  motorLeft.voltage_limit = 0.0;
  motorRight.voltage_limit = 0.0;
}

void motorsOn() {
  motorLeft.voltage_limit = VOLTAGE_LIMIT;
  motorRight.voltage_limit = VOLTAGE_LIMIT;
}

Commander command = Commander(Serial);
void doRight(char* cmd) { 
  Serial.println("right");
  motorsOn();
  Left = 1.0;
  Right = -1.0;
}

void doLeft(char* cmd) { 
  Serial.println("left");
  motorsOn();
  Left = -1.0;
  Right = 1.0;
}

void doGo(char* cmd) { 
  Serial.println("go");
  motorsOn();
  Left = -1.7;
  Right = -1.7;
}

void doStop(char* cmd) { 
  Serial.println("stop");
  motorsOff();
  Left = 0.0;
  Right = 0.0;
}

void doBack(char* cmd) { 
  Serial.println("back");
  motorsOn();
  Left = 1.2;
  Right = 1.2;
}


void setup() {

  Serial.begin(115200);

  delay(1000);

  pinMode(USART1_RX, INPUT);
  analogWriteFrequency(25000);

  // remote.begin(Serial1);
  
  pinMode(LED_PIN, OUTPUT);
  
  digitalWrite(LED_PIN, HIGH);
  delay(50);
  digitalWrite(LED_PIN, LOW);
  delay(50);
  digitalWrite(LED_PIN, HIGH);
  delay(200);

  driverLeft.voltage_power_supply = 12;
  driverLeft.init();
  driverRight.voltage_power_supply = 12;
  driverRight.init();
  
  
  digitalWrite(LED_PIN, HIGH);
  delay(50);
  digitalWrite(LED_PIN, LOW);
  delay(50);
  digitalWrite(LED_PIN, HIGH);
  delay(200);

  // link the motorLeft and the driverLeft
  motorLeft.linkDriver(&driverLeft);
  motorLeft.voltage_limit = 0; //VOLTAGE_LIMIT;   // [V]
  motorLeft.voltage_sensor_align = 4.0;   // [V]
  motorLeft.velocity_limit = 7;
  motorLeft.useMonitoring(Serial);

  motorLeft.controller = MotionControlType::velocity_openloop;

  motorRight.linkDriver(&driverRight);
  motorRight.voltage_limit = 0; //VOLTAGE_LIMIT;   // [V]
  motorRight.voltage_sensor_align = 4.0;   // [V]
  motorRight.velocity_limit = 7;
  motorRight.useMonitoring(Serial);

  motorRight.controller = MotionControlType::velocity_openloop;

  // // init motorLeft hardware
  motorLeft.sensor_offset = -2;
  motorLeft.init();

  motorRight.sensor_offset = 1.5;
  motorRight.init();

  delay(2000);

  // // add target command T
  command.add('l', doLeft, "left");
  command.add('r', doRight, "right");
  command.add('s', doStop, "stop");
  command.add('g', doGo, "go");
  command.add('b', doBack, "back");

}

void loop() {

  float left = lpf_left(Left);
  float right = lpf_right(Right);
  
  motorLeft.move(MAX_SPEED * left);
  motorLeft.loopFOC();

  motorRight.move(MAX_SPEED * right);
  motorRight.loopFOC();

  command.run();

  static long last = 0;
  long now = millis();

  if (now - last > 200) {
    Serial.print(".");
    last = now;
  }
  
}
