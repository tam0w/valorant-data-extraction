import cv2 as cv, easyocr, tkinter as tk, numpy as np, matplotlib.pyplot as plt
from tkinter import ttk, filedialog as fd, font

root = tk.Tk()
root.title('SCRIM ANALYSIS')
param = ("Bahnschrift", 24)
window_width = 700
window_height = 450

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(False, False)

# Import the tcl file
root.tk.call('source', r'D:\PROJECTS\demo-analysis-timeline\desktop-app\forest\forest-dark.tcl')
s = ttk.Style()
# Set the theme with the theme_use method
s.theme_use('forest-dark')
root.attributes('-topmost', 1)
root.iconbitmap(r'D:\PROJECTS\demo-analysis-timeline\res\ico.ico')

welc = tk.Label(root,text="WELCOME", font=param)
welc.pack(pady=10)

exit_button = ttk.Button(root, style='Accent.TButton', text='Exit', command=lambda: root.quit())
exit_button.pack(pady=10)

# A themed (ttk) button
# button = ttk.Button(root, text="I'm a themed button")
# button.pack(pady=20)

root.mainloop()
