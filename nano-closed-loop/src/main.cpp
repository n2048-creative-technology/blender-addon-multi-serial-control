#include <AccelStepper.h>
#include <Wire.h>
#define AS5600_ADDR 0x36  // I2C address of the AS5600

const int debug = 0;

// Pin Definitions
const int stepPin = 2;       // Step pin connected to the motor driver
const int dirPin = 3;        // Direction pin connected to the motor driver
const int enablePin = 4;     // Enable pin connected to the motor driver
const int alarmPin = 5;      // Alarm pin connected to the motor driver

const int sw0Pin = 6; 
const int sw1Pin = 7; 
const int sw2Pin = 8;
const int sw3Pin = 9;

const int dio0Pin = 10; // Limit switch
const int dio1Pin = 11; // Encoder DIR, leave LOW
const int dio2Pin = 12; // SDA encoder
const int dio3Pin = 13; // SCL encoder

//**************************************************
//**************************************************
// EDIT this values for every joint independently
//**************************************************

const int aio0Pin = A0;
const int aio1Pin = A1;
const int aio2Pin = A2;
const int aio3Pin = A3;


// Interval in milliseconds (1000ms = 1 second)
const unsigned long interval = 1000;
unsigned long previousMillis = 0;  // Stores the last time the event was triggered

// Define the AccelStepper interface type for a driver (with step and direction pins)
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

bool prevAlarmState = LOW;

float curTarget = 0;
float curPos = 0;
float prevPos = 0;
float prevTarget = 0;

uint16_t position = 0; // p[osition from magnetic encoder

unsigned long lastSpeedUpdateTime = millis();  

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 100;  // 50ms debounce time

unsigned long lastCommandTime = 0;

float maxSpeed = 4000;
float minSpeed = 10;

 
void disableStepper(){
  digitalWrite(enablePin, HIGH);
}
void enableStepper(){
  digitalWrite(enablePin, LOW);
}

void printPos(){
  long currentStepperPos = stepper.currentPosition();
  Serial.print("target: ");
  Serial.print(curTarget);
  Serial.print(", encoderPos: ");
  Serial.print(position);
  Serial.print(", stepperPos: ");
  Serial.println(currentStepperPos);

}

void checkSerial() {
  if (Serial.available()) {
      String input = Serial.readStringUntil('\n'); // Read until newline character
      input.trim(); // Remove any trailing newline or spaces

      // Split the input string into tokens
      int firstDelim = input.indexOf('|');
      int secondDelim = input.indexOf('|', firstDelim + 1);

      if (firstDelim != -1 && secondDelim != -1) {
          String objName = input.substring(0, firstDelim);
          String paramName = input.substring(firstDelim + 1, secondDelim);
          float value = input.substring(secondDelim + 1).toFloat();

          // Set curTarget with the extracted value
          curTarget = value;

          // Debug output
          if(debug){
            Serial.print("Object: "); Serial.println(objName);
            Serial.print("Parameter: "); Serial.println(paramName);
            Serial.print("Value: "); Serial.println(curTarget);
          }
      }   
  }
}


void scanI2CDevices() {
  byte error, address;
  int nDevices = 0;
  
  if(debug) Serial.println("Scanning for I2C devices on Wire1...");
  for (address = 1; address < 127; address++) {
    Wire1.beginTransmission(address);
    error = Wire1.endTransmission();
    
    if (error == 0) {
      if(debug){ Serial.print("I2C device found at address 0x");
        if (address < 16) Serial.print("0");
        Serial.print(address, HEX);
        Serial.println(" !");
      }
      nDevices++;
    }
  }
  if(debug) {
    if (nDevices == 0) Serial.println("No I2C devices found");
    else Serial.println("done");
  }
}



void checkAlarm(){
  // Check alarm pin status
  bool alarmState = digitalRead(alarmPin);
  if(alarmState != prevAlarmState){
    if (alarmState == LOW) {
      // If alarm is triggered, disable motor
      digitalWrite(enablePin, HIGH);  // Disable the motor
      if(debug) Serial.println("Motor Alarm Triggered. Motor Disabled");
    } else {
      // If no alarm, enable motor
      if(debug) Serial.println("Motor Alarm Deactivated! Motor Enabled.");
      digitalWrite(enablePin, LOW);   // Enable the motor
    }
    prevAlarmState = alarmState;
  }
}

void setup() {
 
  // Encoder direction:
  pinMode(dio1Pin, OUTPUT);
  digitalWrite(dio1Pin, LOW);
  
  // Begin the second I2C bus (Wire1) with custom pins
  Wire1.begin(dio2Pin, dio3Pin);  // Custom pins for second I2C bus: SDA = GPIO 12, SCL = GPIO 13
  
  Serial.begin(115200);  // Initialize serial communication for debugging

  // Set enable pin as output
  pinMode(enablePin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  
  // Set alarm pin as input with internal pull-up
  pinMode(alarmPin, INPUT_PULLUP);

  // Enable the motor initially
  //digitalWrite(enablePin, LOW);

  enableStepper();

  stepper.setSpeed(0);
  // Set max speed and acceleration
  stepper.setMaxSpeed(maxSpeed); // Adjust max speed as necessary
  stepper.setAcceleration(maxSpeed); // Adjust acceleration as necessary

  stepper.setPinsInverted(false, false, false);  // Invert only the direction pin
  stepper.setCurrentPosition(0);

  scanI2CDevices();

  
}


void loop() {

  checkSerial();

  if(debug){
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
      // Save the current time as the last triggered time
      previousMillis = currentMillis;

      // Execute the task every second
      Serial.println("alive!");
    }
  }

  // Read the AS5600 position (just an example, specific AS5600 communication would depend on library or datasheet)
  Wire1.beginTransmission(AS5600_ADDR);
  Wire1.write(0x0C);  // Address of the position register
  Wire1.endTransmission();
  
  Wire1.requestFrom(AS5600_ADDR, 2);

  if (Wire1.available() >= 2) {
    position = Wire1.read() << 8 | Wire1.read();
    curPos = (float)position;
 
    if (debug) printPos();

    unsigned long currentTime = millis();
    
    checkAlarm();

    // If motor is enabled, run the stepper to the target position
    if (digitalRead(enablePin) == LOW) { 
      long dt = currentTime - lastSpeedUpdateTime;
      lastSpeedUpdateTime = millis();

      float err = curTarget-position;
      //Serial.println(err);
      if(abs(err)>10){
        stepper.setSpeed(curTarget-position);
        //stepper.moveTo(curTarget);
        stepper.runSpeed();
      }
    }
        
  }

}