#include <Servo.h>
#include <NewPing.h>

// Motor pins
const int IN1 = 7; // left forward
const int IN2 = 6; // left backward
const int IN3 = 5; // right forward
const int IN4 = 4; // right backward

// Servo and ultrasonic
const int SERVO_PIN = 10;
const int TRIG_PIN  = 9;
const int ECHO_PIN  = 11;
const int MAX_DIST  = 150; // cm

Servo servoMotor;
NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DIST);

void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  servoMotor.attach(SERVO_PIN);
  servoMotor.write(90); // center
  delay(500);
}

void moveForward() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

int readDist() {
  int cm = sonar.ping_cm();
  if (cm == 0) cm = 250; // out-of-range fallback
  return cm;
}

int lookRight() {
  servoMotor.write(45); // adjust if needed for your mounting
  delay(350);
  int d = readDist();
  servoMotor.write(90);
  delay(150);
  return d;
}

int lookLeft() {
  servoMotor.write(135); // adjust if needed
  delay(350);
  int d = readDist();
  servoMotor.write(90);
  delay(150);
  return d;
}

void loop() {
  int front = readDist();
  Serial.print("Front: "); Serial.println(front);

  if (front <= 30) {
    stopMotors();
    delay(200);
    moveBackward();
    delay(400);
    stopMotors();
    delay(200);

    int r = lookRight();
    Serial.print("Right: "); Serial.println(r);
    int l = lookLeft();
    Serial.print("Left: "); Serial.println(l);

    if (r >= l) {
      // turn right: left forward, right backward
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);
      delay(350);
      stopMotors();
    } else {
      // turn left: left backward, right forward
      digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      delay(350);
      stopMotors();
    }
  } else {
    moveForward();
  }

  delay(120);
}