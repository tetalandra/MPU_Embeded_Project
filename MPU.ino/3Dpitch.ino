#include <Wire.h>
const int MPU = 0x68;

float AccX, AccY, AccZ;
float pitch, roll;

void setup() {
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);  // Wake up MPU6050
  Wire.write(0);
  Wire.endTransmission(true);

  Serial.begin(9600);
  Serial.println("MPU6050 Initialized...");
}

void loop() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // Start reading accelerometer
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true);

  int16_t rawX = Wire.read() << 8 | Wire.read();
  int16_t rawY = Wire.read() << 8 | Wire.read();
  int16_t rawZ = Wire.read() << 8 | Wire.read();

  AccX = rawX / 16384.0;
  AccY = rawY / 16384.0;
  AccZ = rawZ / 16384.0;

  // Calculate pitch and roll (in degrees)
  pitch = atan2(AccX, sqrt(AccY*AccY + AccZ*AccZ)) * 180.0 / PI;
  roll  = atan2(AccY, sqrt(AccX*AccX + AccZ*AccZ)) * 180.0 / PI;

  // Send data to Python
  Serial.print(pitch);
  Serial.print(",");
  Serial.println(roll);

  delay(100); // 10 Hz
}
