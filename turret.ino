#include <Servo.h>

const int LEFT_MOVE_PIN_TRIGGER = 10;
const int LEFT_MOVE_PIN_ECHO = 11;

const int RIGHT_MOVE_PIN_TRIGGER = 12;
const int RIGHT_MOVE_PIN_ECHO = 13;


const int SERVO_ROTATE_TURRET = 9;
const int SERVO_TRIGGER_GUN = 8;
const double THRESHOLD_DIST = 30.0;
const int MIN_READS = 10;
int pos = 90;
int control = 1;

Servo rotation_servo;
Servo trigger_servo;

long readUltrasonicDistance(int triggerPin, int echoPin)
{
  pinMode(triggerPin, OUTPUT);  // Clear the trigger
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  // Sets the trigger pin to HIGH state for 10 microseconds
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  // Reads the echo pin, and returns the sound wave travel time in microseconds
  return pulseIn(echoPin, HIGH);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  rotation_servo.attach(SERVO_ROTATE_TURRET);
  trigger_servo.attach(SERVO_TRIGGER_GUN);

  rotation_servo.write(90);
  trigger_servo.write(90);
}

void loop() {
  // put your main code here, to run repeatedly:

  if(Serial.available()){
     String received = Serial.readStringUntil('\n'); // Read command
      received.trim(); // Remove extra spaces or newlines
    if(received.equals("CHANGE"))
      control = 1 - control;
  }

  if(control == 1){
    //read incoming data from python
    if (Serial.available() > 0) {
      String received = Serial.readStringUntil('\n'); // Read command
      received.trim(); // Remove extra spaces or newlines
      // Check for commands with "CMD:" prefix
      if (received.startsWith("CMD:")) {
        received.remove(0, 4); // Remove "CMD:" prefix
        if(received.equals("MOVE_LEFT")){
            if(pos > 30){
              --pos;
              rotation_servo.write(pos);
            }
        }
        else if(received.equals("MOVE_RIGHT")){
          if(pos < 150){
            ++pos;
            rotation_servo.write(pos);
          }
        }
        else if(received.equals("SHOOT")){
          trigger_servo.write(180);
          delay(1000);
          trigger_servo.write(0);
        }
      }
    }
  }
  if(control == 0){
    double distance_left = 0.01723 * readUltrasonicDistance(LEFT_MOVE_PIN_TRIGGER, LEFT_MOVE_PIN_ECHO);
    double distance_right = 0.01723 * readUltrasonicDistance(RIGHT_MOVE_PIN_TRIGGER, RIGHT_MOVE_PIN_ECHO);
    Serial.println(distance_left);
    Serial.println(distance_right);
    Serial.println();
    bool move_left = (distance_left <= THRESHOLD_DIST);
    bool move_right = (distance_right <= THRESHOLD_DIST);

    if(move_left && !move_right){
      if(pos > 30){
        --pos;
        rotation_servo.write(pos);
      }
    }
    else if(!move_left && move_right){
      if(pos < 150){
        ++pos;
        rotation_servo.write(pos);
      }
    }
    else if(move_left && move_right){
      trigger_servo.write(180);
      delay(1000);
      trigger_servo.write(0);
    }
    else{
      rotation_servo.write(pos);
    }
  }
}
