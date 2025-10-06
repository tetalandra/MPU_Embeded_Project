import serial
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# ---- CONFIG ----
PORT = 'COM3'
BAUD = 9600
ser = serial.Serial(PORT, BAUD)
time.sleep(2)

# ---- 3D PLOT SETUP ----
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(0, 2)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Bucket Pitch & Roll Visualization")

# ---- Define bucket vertices ----
def create_bucket():
    # Bucket base (rectangle)
    w, d, h = 1.0, 1.0, 1.2
    base = np.array([
        [-w/2, -d/2, 0],
        [ w/2, -d/2, 0],
        [ w/2,  d/2, 0],
        [-w/2,  d/2, 0],
        [-w/2, -d/2, h],
        [ w/2, -d/2, h],
        [ w/2,  d/2, h],
        [-w/2,  d/2, h],
    ])
    return base

bucket_vertices = create_bucket()

# ---- Define faces for Poly3DCollection ----
def make_faces(v):
    return [
        [v[0], v[1], v[2], v[3]],  # bottom
        [v[4], v[5], v[6], v[7]],  # top
        [v[0], v[1], v[5], v[4]],  # front
        [v[1], v[2], v[6], v[5]],  # right
        [v[2], v[3], v[7], v[6]],  # back
        [v[3], v[0], v[4], v[7]],  # left
    ]

bucket_faces = make_faces(bucket_vertices)
bucket = Poly3DCollection(bucket_faces, facecolors='orange', edgecolors='k', alpha=0.8)
ax.add_collection3d(bucket)

# ---- Rotation matrices ----
def rotation_matrix(pitch, roll):
    pitch_rad = np.radians(pitch)
    roll_rad  = np.radians(roll)

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll_rad), -np.sin(roll_rad)],
        [0, np.sin(roll_rad),  np.cos(roll_rad)]
    ])
    Ry = np.array([
        [ np.cos(pitch_rad), 0, np.sin(pitch_rad)],
        [0, 1, 0],
        [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]
    ])
    return Ry @ Rx  # first roll, then pitch

# ---- Rotate vertices ----
def rotate_vertices(vertices, pitch, roll):
    R = rotation_matrix(pitch, roll)
    return np.array([R @ v for v in vertices])

# ---- Main loop ----
plt.ion()
plt.show()
while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if "," not in line:
                continue
            pitch, roll = map(float, line.split(","))

            rotated_vertices = rotate_vertices(bucket_vertices, pitch, roll)
            rotated_faces = make_faces(rotated_vertices)
            bucket.set_verts(rotated_faces)

            fig.canvas.draw()
            fig.canvas.flush_events()

            print(f"Pitch: {pitch:.2f}, Roll: {roll:.2f}")

    except KeyboardInterrupt:
        print("Stopped by user")
        break
    except:
        continue

ser.close()
