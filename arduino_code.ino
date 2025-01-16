// Define pin for pulse sensor
const int PULSE_SENSOR_PIN = A0;  // Analog Pin 0

// Variables
int Signal;                // Holds the incoming raw data
int BPM;                  // Holds the final BPM

void setup() {
  Serial.begin(9600);     // Initialize serial communication
}

void loop() {
  // Read the sensor value
  Signal = analogRead(PULSE_SENSOR_PIN);
  
  // Convert analog reading to BPM range
  BPM = map(Signal, 0, 1023, 40, 200);
  
  // Send data to Serial monitor
  Serial.print("BPM:");
  Serial.println(BPM);
  
  delay(20);
} 