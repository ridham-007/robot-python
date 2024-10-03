from fastapi import FastAPI, BackgroundTasks
import pyautogui
import time
import random
from threading import Event

app = FastAPI()

# Flag to control the mouse juggling loop
stop_event = Event()

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
        background_tasks.add_task(start_juggling)  # Run juggling in the background
        return {"message": "Mouse juggling started!"}
    return {"message": "Mouse juggling is already running!"}

@app.post("/stop")
async def stop():
    stop_event.set()  # Set the stop flag to stop the loop
    return {"message": "Mouse juggling stopped!"}
