from fastapi import FastAPI, BackgroundTasks
import pyautogui    
import time
import random
import numpy as np
from threading import Event

app = FastAPI()

# Flag to control the mouse juggling loop
stop_event = Event()

def move_mouse_exponential_to_random(duration=1.0, steps=10):
    
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
    
    # Move the mouse pointer along the calculated points
    start_time = time.time()
    for x, y in zip(x_positions, y_positions):
        pyautogui.moveTo(x, y)
        elapsed_time = time.time() - start_time
        if elapsed_time < duration:
            time.sleep(duration / steps)
    
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
