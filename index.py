import pyautogui
import time
import random

def move_mouse(n, speed):
    pyautogui.moveRel(n, n, duration=speed)
    pyautogui.moveRel(-n, -n, duration=speed)

def press_key(key):
    pyautogui.press(key)

def mouse_juggling(n, speed, interval, click_interval, keys, inter):
    move_mouse(n, speed)
    move_mouse(-n, speed)
    
    # Calculate the total number of events to be generated
    total_events = len(keys)
    
    # Generate random numbers of mouse and key events between 0 and total_events
    num_mouse_events = random.randint(0, total_events)
    num_key_events = total_events - num_mouse_events
    
    if time.time() % click_interval < 0.02:
        if num_mouse_events > 0 and num_key_events > 0:
            action = random.choice(['mouse_click', 'key_press'])
        elif num_mouse_events > 0:
            action = 'mouse_click'
        elif num_key_events > 0:
            action = 'key_press'
        else:
            return  # No events to perform
        
        if action == 'mouse_click':
            button = random.choice(['left', 'right', 'middle'])
            pyautogui.click(button=button)
            num_mouse_events -= 1

        elif action == 'key_press':
            key = random.choice(keys)
            numOfTab = random.choice([1, 2, 3, 4])
            if inter == 9:
                for i in range(random.choice([10, 20, 30])):
                    pyautogui.press(random.choice(['up', 'down', 'left', 'right']))

            if key == 'changeTab':
                pyautogui.keyDown('ctrl')
                for i in range(numOfTab):
                    pyautogui.press('tab')
                pyautogui.keyUp('ctrl')

            elif key == 'changeScreen':
                pyautogui.keyDown('alt')
                for i in range(numOfTab):
                    pyautogui.press('tab')
                pyautogui.keyUp('alt')

            else:
                press_key(key)
            num_key_events -= 1
    time.sleep(interval)

keys = ['up', 'down', 'left', 'right', 'changeTab', 'multiple']  # define the keys and mouse actions
while True:
    for i in range(len(keys)):  # repeat for each key/mouse action
        mouse_juggling(5, 0.03, 0.2, 0.03, keys, i)  # interval reduced to 0.001 second, click every 0.01 second
    time.sleep(0.02)  # move the mouse every 0.02 seconds