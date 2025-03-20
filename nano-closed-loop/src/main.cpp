#include <AccelStepper.h>
#include <Wire.h>

#define AS5600_ADDR 0x36  // I2C address of the AS5600
#define RAW_ANGLE_REG 0x0C

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


int last_position = 0;
bool first_read = true;

bool prevAlarmState = LOW;

float curTarget = 0;
float curPos = 0;
float prevPos = 0;
float prevTarget = 0;
bool enabled = 1;

uint16_t position = 0; // p[osition from magnetic encoder

unsigned long lastSpeedUpdateTime = millis();  

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 100;  // 50ms debounce time

unsigned long lastCommandTime = 0;

float maxSpeed = 4000;
float minSpeed = 10;
 
void disableStepper(){
  enabled=false;
  digitalWrite(enablePin, HIGH);
}

void enableStepper(){
  enabled=true;
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
          objName.trim();

          String paramName = input.substring(firstDelim + 1, secondDelim);
          paramName.trim();

          float value = input.substring(secondDelim + 1).toFloat();

          if(paramName=="learn_mode") {
            disableStepper();
            if(prevPos != curPos){
              Serial.println(curPos);
              Serial.flush();
            }      
          }
          else {
            enableStepper();
            // Set curTarget with the extracted value
            curTarget = value;
          }

          // Debug output
          if(debug){
            Serial.print("input: "); Serial.println(input);
            Serial.print("Object: "); Serial.println(objName);
            Serial.print("Parameter: "); Serial.println(paramName);
            Serial.print("Value: "); Serial.println(curTarget);
          }
      }   
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

void readRawAngle() {
  Wire1.beginTransmission(AS5600_ADDR);
  Wire1.write(RAW_ANGLE_REG);
  Wire1.endTransmission();

  Wire1.requestFrom(AS5600_ADDR, 2);
  
  if (Wire1.available() == 2) {
    int position = Wire1.read() << 8 | Wire1.read();

    if (position == -1) {
      Serial.println("Error reading AS5600");
      return;
    }

    if (first_read) {
        last_position = position;
        first_read = false;
    }

    int delta = position - last_position;

    // Detect wrap-around
    if (delta > 2048) {  
        // Counterclockwise wrap (e.g., 10 → 4090)
        curPos -= (4096 - delta);
    } 
    else if (delta < -2048) {  
        // Clockwise wrap (e.g., 4090 → 10)
        curPos += (4096 + delta);
    } 
    else {
        // Normal movement
        curPos += delta;
    }

    last_position = position;
  }
  else{
    Serial.println("no i2c data from AS5600");
  }
}

void setup() {
 
  // Encoder direction:
  pinMode(dio1Pin, OUTPUT);
  digitalWrite(dio1Pin, LOW);
  
  // Begin the second I2C bus (Wir1) with custom pins
  //Wire.begin(); 
  Wire1.begin(dio2Pin, dio3Pin); 

  Serial.println("Error reading AS5600");

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
      Serial.print("curTarget: ");
      Serial.println(curTarget);
      Serial.print("curPos: ");
      Serial.println(curPos);
    }
  }

  readRawAngle();
  
  checkAlarm();

  // If motor is enabled, run the stepper to the target position
  if (enabled) { 
    float err = curTarget-curPos;
    //Serial.println(err);
    if(abs(err)>0){
      stepper.setSpeed(curTarget-curPos);
      //stepper.moveTo(curTarget);
    }
  }
  else{
    Serial.println(curPos);
    delay(1000/60);
  }
  prevPos=curPos;

  prevTarget= curTarget;  

  stepper.runSpeed();

}