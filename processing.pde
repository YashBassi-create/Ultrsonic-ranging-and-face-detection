import processing.serial.*;

Serial myPort;
String data = "";
int angle = 0, distance = 0;
boolean objectDetected = false;

void setup() {
  size(800, 450);
  myPort = new Serial(this, "COM5", 9600);
  myPort.bufferUntil('\n');
  textAlign(CENTER);
  smooth();
}

void draw() {
  background(0);
  translate(width/2 - 50, height);

  // radar grid
  stroke(0, 255, 0);
  noFill();
  for (int i = 1; i <= 4; i++) ellipse(0, 0, i * 200, i * 200);
  for (int i = 0; i <= 180; i += 30) {
    float x = 400 * cos(radians(i));
    float y = -400 * sin(radians(i));
    line(0, 0, x, y);
  }

  // beam color based on detection
  if (objectDetected) {
    stroke(255, 0, 0, 180); // red
  } else {
    stroke(0, 255, 0, 180); // green
  }

  float x = 400 * cos(radians(angle));
  float y = -400 * sin(radians(angle));
  line(0, 0, x, y);

  // draw detected point
  if (distance < 100) {
    float px = distance * 4 * cos(radians(angle));
    float py = -distance * 4 * sin(radians(angle));
    fill(255, 0, 0);
    noStroke();
    ellipse(px, py, 10, 10);
  }

  // bottom info
  resetMatrix();
  fill(0);
  rect(0, height - 40, width, 40);
  fill(objectDetected ? color(255, 0, 0) : color(0, 255, 0));
  textSize(16);
  textAlign(LEFT);
  text("Simple Radar", 20, height - 15);
  textAlign(CENTER);
  text("Angle: " + angle + "°", width / 2, height - 15);
  textAlign(RIGHT);
  text("Distance: " + distance + " cm", width - 20, height - 15);
}

void serialEvent(Serial p) {
  data = p.readStringUntil('\n');
  if (data != null) {
    data = trim(data);
    String[] values = split(data, ',');
    if (values.length == 2) {
      angle = int(values[0]);
      distance = int(values[1]);
      objectDetected = (distance < 100);
    }
  }
}
