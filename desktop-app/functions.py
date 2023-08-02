import time

import pyautogui as py


print(py.size())
rounds = []
time.sleep(3)

print(py.position())

py.moveTo(1020,190,duration=0.5)
py.leftClick()

py.moveTo(187,333,duration=0.45)
py.leftClick()

for i in range(23):
    py.moveRel(63,0,duration=0.2)
    py.leftClick()
    if i == 11:
        py.moveRel(-20, 0, duration=0.2)
