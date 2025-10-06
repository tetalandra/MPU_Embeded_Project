import math
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

# ---------- CONFIGURATION ----------
PORT = 'COM3'   # Change this to your Arduino COM port
BAUD = 115200
WINDOW = 200
ser = serial.Serial(PORT, BAUD, timeout=1)

pitch_buf = deque(maxlen=WINDOW)
roll_buf  = deque(maxlen=WINDOW)
yaw_buf   = deque(maxlen=WINDOW)
x_idx     = deque(maxlen=WINDOW)

fig = plt.figure(figsize=(10, 6))

# --- Plot 1: Pitch, Roll, Yaw ---
ax1 = fig.add_subplot(2, 1, 1)
(line_pitch,) = ax1.plot([], [], label="Pitch (°)")
(line_roll,)  = ax1.plot([], [], label="Roll (°)")
(line_yaw,)   = ax1.plot([], [], label="Yaw (°)")
ax1.set_xlim(0, WINDOW)
ax1.set_ylim(-180, 180)
ax1.set_xlabel("Samples")
ax1.set_ylabel("Angle (°)")
ax1.set_title("MPU6050 Pitch, Roll & Yaw")
ax1.legend(loc="upper right")

# --- Plot 2: 3D Bucket ---
ax2 = fig.add_subplot(2, 1, 2, projection="3d")
ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.set_zlim(-2, 2)
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("Z")
ax2.set_title("3D Realistic Bucket with Handle")

# ---------- BUCKET CREATION ----------
def create_realistic_bucket(r_bottom=0.5, r_top=0.8, height=1.2, thickness=0.05, segments=40):
    faces = []
    angles = np.linspace(0, 2*np.pi, segments, endpoint=False)

    # outer and inner vertices
    outer_bottom = np.array([[r_bottom*np.cos(a), r_bottom*np.sin(a), -height/2] for a in angles])
    outer_top    = np.array([[r_top*np.cos(a), r_top*np.sin(a), height/2] for a in angles])
    inner_bottom = np.array([[(r_bottom-thickness)*np.cos(a), (r_bottom-thickness)*np.sin(a), -height/2] for a in angles])
    inner_top    = np.array([[(r_top-thickness)*np.cos(a), (r_top-thickness)*np.sin(a), height/2] for a in angles])

    # outer walls
    for i in range(segments):
        j = (i+1) % segments
        faces.append([outer_bottom[i], outer_bottom[j], outer_top[j], outer_top[i]])

    # inner walls
    for i in range(segments):
        j = (i+1) % segments
        faces.append([inner_top[i], inner_top[j], inner_bottom[j], inner_bottom[i]])

    # bottom
    for i in range(segments):
        j = (i+1) % segments
        faces.append([outer_bottom[i], outer_bottom[j], inner_bottom[j], inner_bottom[i]])

    # rim
    for i in range(segments):
        j = (i+1) % segments
        faces.append([outer_top[i], outer_top[j], inner_top[j], inner_top[i]])

    # colors
    colors = (
        ['deepskyblue'] * segments +      # outer wall
        ['lightgray'] * segments +        # inner wall
        ['dimgray'] * segments +          # bottom
        ['silver'] * segments             # rim
    )

    return faces, colors, outer_top

# ---------- HANDLE CREATION ----------
def create_handle(outer_top, height=1.2):
    # pick two opposite rim points
    left = outer_top[0]
    right = outer_top[len(outer_top)//2]

    # arc points for handle (semicircle)
    num_points = 40
    handle_pts = []
    for t in np.linspace(0, np.pi, num_points):
        x = (left[0] + right[0]) / 2 + (right[0] - left[0]) / 2 * np.cos(t)
        y = (left[1] + right[1]) / 2 + (right[1] - left[1]) / 2 * np.cos(t)
        z = height/2 + np.sin(t) * (height/1.2)
        handle_pts.append([x, y, z])

    handle_pts = np.array(handle_pts)
    return handle_pts

# ---------- INITIAL SETUP ----------
bucket_faces, bucket_colors, outer_top = create_realistic_bucket()
bucket = Poly3DCollection(bucket_faces, facecolors=bucket_colors, edgecolors='k', alpha=0.9)
ax2.add_collection3d(bucket)

handle_pts = create_handle(outer_top)
(handle_line,) = ax2.plot(handle_pts[:,0], handle_pts[:,1], handle_pts[:,2], color='darkgray', linewidth=3)

# ---------- ROTATION ----------
def rotation_matrix(pitch, roll, yaw):
    pitch_rad = np.radians(pitch)
    roll_rad = np.radians(roll)
    yaw_rad = np.radians(yaw)

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(roll_rad), -np.sin(roll_rad)],
                   [0, np.sin(roll_rad), np.cos(roll_rad)]])
    Ry = np.array([[np.cos(pitch_rad), 0, np.sin(pitch_rad)],
                   [0, 1, 0],
                   [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]])
    Rz = np.array([[np.cos(yaw_rad), -np.sin(yaw_rad), 0],
                   [np.sin(yaw_rad), np.cos(yaw_rad), 0],
                   [0, 0, 1]])
    return Rz @ Ry @ Rx

def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 3:
            return None, None, None
        return float(parts[0]), float(parts[1]), float(parts[2])
    except:
        return None, None, None

def init():
    line_pitch.set_data([], [])
    line_roll.set_data([], [])
    line_yaw.set_data([], [])
    return line_pitch, line_roll, line_yaw, bucket, handle_line

def update(frame):
    global bucket, handle_pts
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            break
        pitch, roll, yaw = parse_line(raw)
        if pitch is None:
            continue
        pitch_buf.append(pitch)
        roll_buf.append(roll)
        yaw_buf.append(yaw)
        x_idx.append(len(x_idx) + 1 if x_idx else 1)

    xs = list(range(len(x_idx)))
    line_pitch.set_data(xs, list(pitch_buf))
    line_roll.set_data(xs, list(roll_buf))
    line_yaw.set_data(xs, list(yaw_buf))
    ax1.set_xlim(max(0, len(xs)-WINDOW), max(WINDOW, len(xs)))

    if pitch_buf and roll_buf and yaw_buf:
        pitch = pitch_buf[-1]
        roll  = roll_buf[-1]
        yaw   = yaw_buf[-1]
        R = rotation_matrix(pitch, roll, yaw)

        # rotate bucket
        faces, colors, outer_top = create_realistic_bucket()
        rotated_faces = []
        for face in faces:
            rotated_faces.append([R @ vertex for vertex in face])
        bucket.set_verts(rotated_faces)
        bucket.set_facecolor(colors)

        # rotate handle
        handle_points_rot = np.array([R @ v for v in create_handle(outer_top)])
        handle_line.set_data(handle_points_rot[:, 0], handle_points_rot[:, 1])
        handle_line.set_3d_properties(handle_points_rot[:, 2])

    return line_pitch, line_roll, line_yaw, bucket, handle_line

ani = animation.FuncAnimation(fig, update, init_func=init, interval=30, blit=False)
plt.tight_layout()
plt.show()
