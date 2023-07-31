import cv2 as cv, easyocr, tkinter as tk, numpy as np, matplotlib.pyplot as plt
from tkinter import ttk

root = tk.Tk()
root.title('SCRIM ANALYSIS')

window_width = 700
window_height = 450

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Import the tcl file
root.tk.call('source', r'D:\PROJECTS\demo-analysis-timeline\desktop-app\forest\forest-dark.tcl')

# Set the theme with the theme_use method
ttk.Style().theme_use('forest-dark')



# A themed (ttk) button
# button = ttk.Button(root, text="I'm a themed button")
# button.pack(pady=20)

root.mainloop()

