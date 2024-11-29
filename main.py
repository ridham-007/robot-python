from fastapi import FastAPI, BackgroundTasks, Query
import pyautogui    
import time
import random
import numpy as np
from threading import Event
import math

app = FastAPI()

# Flag to control the mouse juggling loop
stop_event = Event()

def move_mouse_exponential_to_random(duration=1.0, steps=100):
    # Get current mouse position
    start_x, start_y = pyautogui.position()
    
    # Get screen size to limit random movement within the screen bounds
    screen_width, screen_height = pyautogui.size()
    
    # Generate random target position
    end_x = random.randint(0, screen_width)
    end_y = random.randint(0, screen_height)
    
    # Generate random exponential curve modifiers
    exp_factor = random.uniform(0.5, 2.0)  # Random curve steepness factor
    invert_curve = random.choice([True, False])  # Randomly decide to invert the curve
    
    # Generate time points for the curve, distributed exponentially
    time_points = np.linspace(0, 1, steps)
    if invert_curve:
        curve_points = np.exp(exp_factor * time_points) - 1
    else:
        curve_points = 1 - np.exp(-exp_factor * time_points)
    
    # Normalize the curve points between 0 and 1
    curve_points = (curve_points - curve_points.min()) / (curve_points.max() - curve_points.min())
    
    # Calculate the x and y positions along the curve
    x_positions = start_x + (end_x - start_x) * curve_points
    y_positions = start_y + (end_y - start_y) * curve_points
    
    # Add micro-random variations to simulate human imperfections in mouse movement
    def add_micro_variation(position, intensity=2):
        return position + random.uniform(-intensity, intensity)
    
    # Start the mouse movement
    start_time = time.time()
    for i in range(steps):
        x = add_micro_variation(x_positions[i])
        y = add_micro_variation(y_positions[i])
        pyautogui.moveTo(x, y)
        
        # Compute the time to pause between steps for smoothness
        elapsed_time = time.time() - start_time
        remaining_time = duration - elapsed_time
        if remaining_time > 0:
            time.sleep(remaining_time / (steps - i))
        else:
            break  # Exit if time exceeded the intended duration
    
    print(f"Mouse moved from ({start_x}, {start_y}) to ({end_x}, {end_y})")

# Function to move mouse
def move_mouse(n, speed):
    pyautogui.moveRel(n, n, duration=speed)
    pyautogui.moveRel(-n, -n, duration=speed)

# Function to press a key
def press_key(key):
    pyautogui.press(key)

# The mouse juggling logic
def mouse_juggling(n, speed, interval, click_interval, keys, inter):
    while not stop_event.is_set():
        move_mouse(n, speed)
        move_mouse(-n, speed)
        
        total_events = len(keys)
        num_mouse_events = random.randint(0, total_events)
        num_key_events = total_events - num_mouse_events
        
        if time.time() % click_interval < 0.02:
            action = random.choice(['mouse_click', 'key_press']) if num_mouse_events > 0 and num_key_events > 0 else 'mouse_click' if num_mouse_events > 0 else 'key_press'
            
            if action == 'mouse_click':
                button = random.choice(['left', 'right', 'middle'])
                pyautogui.click(button=button)
                num_mouse_events -= 1
            elif action == 'key_press':
                key = random.choice(keys)
                numOfTab = random.choice([1, 2, 3, 4])
                if inter == 9:
                    for _ in range(random.choice([10, 20, 30])):
                        pyautogui.press(random.choice(['up', 'down', 'left', 'right']))

                if key == 'changeTab':
                    pyautogui.keyDown('ctrl')
                    for _ in range(numOfTab):
                        pyautogui.press('tab')
                    pyautogui.keyUp('ctrl')
                elif key == 'changeScreen':
                    pyautogui.keyDown('alt')
                    for _ in range(numOfTab):
                        pyautogui.press('tab')
                    pyautogui.keyUp('alt')
                else:
                    press_key(key)
                num_key_events -= 1
        time.sleep(interval)

# Background task to run mouse juggling
def start_juggling():
    keys = ['up', 'down', 'left', 'right', 'changeTab', 'multiple']
    for i in range(len(keys)):
        mouse_juggling(5, 0.03, 0.2, 0.03, keys, i)

@app.post("/start")
async def start(background_tasks: BackgroundTasks):
    if stop_event.is_set():  # Check if it was stopped before
        stop_event.clear()  # Clear the stop flag to allow restarting

    if not stop_event.is_set():  # Ensure it's not running
        background_tasks.add_task(move_mouse_exponential_to_random)  # Run juggling in the background
        return {"message": "Mouse juggling started!"}
    return {"message": "Mouse juggling is already running!"}

@app.post("/stop")
async def stop():
    stop_event.set()  # Set the stop flag to stop the loop
    return {"message": "Mouse juggling stopped!"}

@app.post("/click")
async def click_after_delay(
    background_tasks: BackgroundTasks,
    x: int = Query(None, description="X-coordinate of the position"),
    y: int = Query(None, description="Y-coordinate of the position"),
):
    """
    API to move the mouse to a specified position and click after a 2-second delay,
    with human-like random movements including zigzags, curves, wandering, and corrections.
    """
    def delayed_click():
        time.sleep(0.4)  # Reduced delay (was 2 seconds, now ~0.4s)
        screen_width, screen_height = pyautogui.size()

        target_x = x if x is not None else screen_width // 2 - 10
        target_y = y if y is not None else screen_height - 200

        current_x, current_y = pyautogui.position()
        movement_type = random.choice(["parabolic", "wander", "multi_directional"])

        path = []
        if movement_type == "parabolic":
            steps = random.randint(10, 15)  # Smooth, gradual movement
            curve_amplitude = random.randint(100, 100)  # Adjust based on distance
            path = []

            for i in range(steps + 1):
                t = i / steps  # Progress (0 to 1)
                interp_x = current_x + (target_x - current_x) * t
                interp_y = current_y + (target_y - current_y) * t

                # Quadratic parabolic offset for natural curve
                mid_x = (current_x + target_x) / 2
                offset = curve_amplitude * (1 - 4 * ((interp_x - mid_x) / (target_x - current_x))**2)
                path.append((interp_x, interp_y + offset))

            # Only move the cursor to the final target position once
            final_x, final_y = path[-1]  # Get the final point of the path
            pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.2, 0.5))  # Smooth final move
            pyautogui.click()  # Click at the target position after movement

            print(f"Mouse clicked at position ({final_x}, {final_y}) after parabolic movement")
        elif movement_type == "wander":
            num_points = random.randint(2, 3)  # Fewer wander points
            wander_radius = random.randint(30, 80)
            intermediate_points = [
                (
                    current_x + random.randint(-wander_radius, wander_radius),
                    current_y + random.randint(-wander_radius, wander_radius),
                )
                for _ in range(num_points)
            ]
            intermediate_points.append((target_x, target_y))
            for i, (next_x, next_y) in enumerate(intermediate_points):
                steps = random.randint(5, 10)
                for j in range(steps + 1):
                    t = j / steps
                    interp_x = current_x + (next_x - current_x) * t
                    interp_y = current_y + (next_y - current_y) * t
                    path.append((interp_x, interp_y))
                current_x, current_y = next_x, next_y

        elif movement_type == "multi_directional":
            num_segments = random.randint(2, 3)  # Fewer random movements
            for _ in range(num_segments):
                random_x = current_x + random.randint(-50, 50)
                random_y = current_y + random.randint(-50, 50)
                steps = random.randint(5, 8)
                for i in range(steps + 1):
                    t = i / steps
                    interp_x = current_x + (random_x - current_x) * t
                    interp_y = current_y + (random_y - current_y) * t
                    path.append((interp_x, interp_y))
                current_x, current_y = random_x, random_y
            steps = random.randint(10, 15)
            for i in range(steps + 1):
                t = i / steps
                interp_x = current_x + (target_x - current_x) * t
                interp_y = current_y + (target_y - current_y) * t
                path.append((interp_x, interp_y))

        for point in path:
            pyautogui.moveTo(point[0], point[1], duration=random.uniform(0.004, 0.02))  # Increased speed

        pyautogui.click()
        print(f"Mouse clicked at position ({target_x}, {target_y}) after {movement_type} movement")

    background_tasks.add_task(delayed_click)
    return {"message": f"Mouse move (human-like) and click scheduled to happen quickly at ({x}, {y})!"}