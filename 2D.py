import utils.session
import serial
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ---- CONFIG ----
PORT = 'COM3'  # Your Arduino COM port
BAUD = 9600
ser = serial.Serial(PORT, BAUD)
time.sleep(2)  # Wait for Arduino to initialize

# ---- SETUP PLOT ----
fig, ax = plt.subplots()
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.set_title("2D Bucket Pitch Visualization")

# Draw bucket as a rectangle + handle
bucket_width = 1.0
bucket_height = 1.2
handle_radius = 0.5

# Bucket base rectangle (centered at origin)
bucket_rect = patches.Rectangle((-bucket_width/2, -bucket_height/2),
                                bucket_width, bucket_height,
                                facecolor='orange', edgecolor='black')
ax.add_patch(bucket_rect)

# Handle (semi-circle on top)
handle = patches.Arc((0, bucket_height/2), handle_radius*2, handle_radius,
                     theta1=0, theta2=180, color='brown', linewidth=2)
ax.add_patch(handle)

plt.ion()
plt.show()

def rotate_point(x, y, angle_deg):
    """Rotate a point around origin by angle in degrees"""
    angle_rad = np.radians(angle_deg)
    xr = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    yr = x * np.sin(angle_rad) + y * np.cos(angle_rad)
    return xr, yr

def rotate_bucket(angle):
    """Rotate the bucket rectangle and handle"""
    # Rotate rectangle corners
    x0, y0 = -bucket_width/2, -bucket_height/2
    x1, y1 = bucket_width/2, -bucket_height/2
    x2, y2 = bucket_width/2, bucket_height/2
    x3, y3 = -bucket_width/2, bucket_height/2

    corners = np.array([rotate_point(x0,y0,angle),
                        rotate_point(x1,y1,angle),
                        rotate_point(x2,y2,angle),
                        rotate_point(x3,y3,angle)])

    bucket_rect.set_xy(corners[0])
    bucket_rect.set_width(bucket_width)
    bucket_rect.set_height(bucket_height)

    # Update handle position (rotate top center)
    handle_center = rotate_point(0, bucket_height/2, angle)
    handle.angle = angle  # rotates arc visually (approximation)
    handle.set_center(handle_center)

while True:
    try:
        if ser.in_waiting > 0:
            pitch = float(ser.readline().decode().strip())
            rotate_bucket(pitch)
            fig.canvas.draw()
            fig.canvas.flush_events()
            print(f"Pitch: {pitch:.2f}°")
    except KeyboardInterrupt:
        print("Stopped by user")
        break
    except:
        continue

ser.close()
