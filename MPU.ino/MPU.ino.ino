#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;
float pitch, roll, yaw;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
  Serial.println("MPU6050 ready!");
}

void loop() {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Convert accelerometer data to angles
  pitch = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / M_PI;
  roll  = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / M_PI;
  yaw   += gz * (1.0 / 131.0) * 0.01; // simple gyro integration

  // Keep yaw bounded
  if (yaw > 180) yaw -= 360;
  if (yaw < -180) yaw += 360;

  // Send comma-separated pitch, roll, yaw
  Serial.print(pitch, 2);
  Serial.print(",");
  Serial.print(roll, 2);
  Serial.print(",");
  Serial.println(yaw, 2);

  delay(20); // ~50Hz
}
