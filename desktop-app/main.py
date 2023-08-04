import cv2 as cv, easyocr, tkinter as tk, numpy as np, matplotlib.pyplot as plt, pandas as pd
from tkinter import ttk, filedialog as fd, font
from functions import *

def go_timeline():
    py.leftClick(x=1020, y=190, duration=0.35)
    py.leftClick(x=187, y=333, duration=0.3)


def rounds_ss(total_rounds):
    global timestamps
    time.sleep(2)
    go_timeline()
    tl_ss = []

    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    tl_ss.append(cv_image)

    for i in range(total_rounds):

        py.moveRel(63, 0, duration=0.12)
        py.leftClick()

        if i == 11:
            py.moveRel(-20, 0, duration=0.2)
            continue

        image = py.screenshot()
        cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        tl_ss.append(cv_image)

    # The preprocessing and ocr can either be done in this function or another.

    timestamps = rounds_ocr(tl_ss)

    print('test', timestamps)



def scoreboard_ocr():
    py.leftClick(x=875, y=190, duration=0.35)
    scoreboard_ss = py.screenshot()
    scoreboard_ss = cv.cvtColor(np.array(scoreboard_ss), cv.COLOR_RGB2BGR)
    """Any preprocessing or other shenanigans here. And then perform OCR and return match metadata, individual player
    stats aswell as match score / outcome. This can be a data frame. Also distinctly return total no of rounds."""
    # return

def rounds_ocr(all_round_images):
    '''Perform OCR And preprocessing of all the rounds to extract, which player got the first kill, when they get it
    if the spike was planted or not. Possibly in a dataframe?'''

    rounds = pd.DataFrame(['first_kill','time','opponent','planted','round_win'])
    all_round_images_cropped = [images[505:840,980:1040] for images in all_round_images]
    timestamps = [reader.readtext(image,detail=0) for image in all_round_images_cropped]
    print('1',timestamps)
    # Perform your preprocessing and OCR here. If all preprocessing is the same, we can make that a seperate function.
    return timestamps

root = tk.Tk()
root.title('SCRIM ANALYSIS')
root.iconbitmap(r'D:\PROJECTS\demo-analysis-timeline\res\ico.ico')
norm = ("Bahnschrift", 16, 'bold')
param = ("Bahnschrift", 24, 'bold')
window_width = 700
window_height = 500
timestamps = []

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(False, False)
root.tk.call('source', r'D:\PROJECTS\demo-analysis-timeline\desktop-app\forest\forest-dark.tcl')

s = ttk.Style()

s.theme_use('forest-dark')

background_image= tk.PhotoImage(file=r'D:\PROJECTS\demo-analysis-timeline\res\blur3.gif')
can = tk.Canvas(root,width = 700, height = 550)
can.pack(padx=0,pady=0,ipady=50,ipadx=50)
can.create_image(300,250,image=background_image)

welc = tk.Label(can,text="SCRIM ANALYSIS CSV", font=param, fg='#217247', bg="#0F0F0F")
welc.pack(pady=(20,15))

canvas = tk.Canvas(can, height=5, bg="#217247").pack(fill='x', pady=(5,20))

welc1 = tk.Label(can,text="- Open VALORANT.", font=norm, fg='#217247', justify='left', anchor='w', width=100, bg="#0F0F0F")
welc1.pack(pady=3, padx=30)

welc2 = tk.Label(can,text="- Open the scoreboard page for the scrim.", font=norm, fg='#217247', justify='left', anchor='w', width=100, bg="#0F0F0F")
welc2.pack(pady=3, padx=30)

welc3 = tk.Label(can,text="- Press the analyze button.", font=norm, fg='#217247', justify='left', anchor='w', width=100, bg="#0F0F0F")
welc3.pack(pady=3, padx=30)

welc4 = tk.Label(can,text="- Login on the website and download csv.", font=norm, fg='#217247', justify='left', anchor='w', width=100, bg="#0F0F0F")
welc4.pack(pady=3, padx=30)


canvas1 = tk.Canvas(can, height=5, bg="#217247").pack(fill='x', pady=(20,20))

button_border = tk.Frame(can, highlightbackground = "#217247", highlightthickness = 2)
exit_button = tk.Button(button_border, text='Analyze', borderwidth=0, bg="#0F0F0F",fg="#217247", command=lambda: rounds_ss(3), font=param)
exit_button.pack(ipadx=30,ipady=0,side=tk.LEFT)
button_border.pack(pady=20,padx=(20,10),side=tk.LEFT)

button_border1 = tk.Frame(can, highlightbackground = "#217247", highlightthickness = 2)
exit_button1 = tk.Button(button_border1, text='HMMMMMMMMMMMM', borderwidth=0, bg="#0F0F0F",fg="#217247", command=lambda: root.quit(), font=param)
exit_button1.pack(ipadx=30,ipady=0,side=tk.RIGHT)
button_border1.pack(pady=20,padx=(10,20),side=tk.RIGHT)

print(timestamps)

root.mainloop()
