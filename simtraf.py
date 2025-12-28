import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

N_CARS = 20
RADIUS = 5.5
DT = 0.05

V_MAX = 5.0
SAFE_DIST = 1.6
HARD_STOP_DIST = 1.0

REACTION_DELAY = 2
ACCEL = 3.0
MAX_BRAKE = 12.0

MIN_ANGLE_GAP = HARD_STOP_DIST / RADIUS

def optimal_velocity(d):
    return V_MAX * (np.tanh(6 * (d - SAFE_DIST)) + 1) / 2

angles = np.linspace(0, 2 * np.pi, N_CARS, endpoint=False)
angles += 0.1 * np.random.randn(N_CARS)
angles = np.sort(angles)
speeds = np.ones(N_CARS) * V_MAX * 0.9
speed_memory = [speeds.copy()]

def step():
    global angles, speeds, speed_memory

    delayed = speed_memory[-REACTION_DELAY] if len(speed_memory) >= REACTION_DELAY else speeds

    new_speeds = speeds.copy()
    proposed_angles = angles.copy()

    for i in range(N_CARS):
        lead = (i + 1) % N_CARS

        gap = angles[lead] - angles[i]
        if gap <= 0:
            gap += 2 * np.pi

        dist = RADIUS * gap

        if dist < HARD_STOP_DIST:
            new_speeds[i] = 0.0
            continue

        target = optimal_velocity(dist)
        dv = ACCEL * (target - delayed[i])
        dv = np.clip(dv, -MAX_BRAKE, ACCEL)
        new_speeds[i] += dv * DT

    new_speeds = np.clip(new_speeds, 0, V_MAX)

    for i in range(N_CARS):
        proposed_angles[i] += new_speeds[i] * DT / RADIUS

    for i in range(N_CARS - 1):
        max_allowed = proposed_angles[i + 1] - MIN_ANGLE_GAP
        if proposed_angles[i] > max_allowed:
            proposed_angles[i] = max_allowed
            new_speeds[i] = 0.0

    if proposed_angles[-1] > proposed_angles[0] + 2 * np.pi - MIN_ANGLE_GAP:
        proposed_angles[-1] = proposed_angles[0] + 2 * np.pi - MIN_ANGLE_GAP
        new_speeds[-1] = 0.0

    angles[:] = proposed_angles % (2 * np.pi)
    speeds[:] = new_speeds[:]

    speed_memory.append(speeds.copy())
    if len(speed_memory) > 10:
        speed_memory.pop(0)

plt.ion()
fig, ax = plt.subplots(figsize=(6, 6))

while True:
    step()
    ax.clear()

    ax.add_patch(plt.Circle((0, 0), RADIUS, fill=False, linewidth=3))

    for i in range(N_CARS):
        x = RADIUS * np.cos(angles[i])
        y = RADIUS * np.sin(angles[i])

        ax.scatter(
            x, y,
            c=speeds[i],
            cmap="coolwarm",
            vmin=0,
            vmax=V_MAX,
            s=220,
            edgecolors="black"
        )

    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Calle Singular de Tráfico", fontsize=14)

    plt.pause(0.02)
