import cv2 as cv, easyocr, tkinter, numpy as np, matplotlib.pyplot as plt

reader = easyocr.Reader(['en'])

# def preprocessing(img):
#     """ Perfrom all the image preprocessing here. Not sure how to handle different images needing different preprocessing
#     but lets see."""
#     return finalimg
#
# def run_ocr(img):
#     result = reader.readtext(img, detail=0)
#     return result


ogfile = cv.imread('frame.png')
# cv.imshow('test',file[50:200,50:200])
file = ogfile[50:200,50:200]
gray = cv.cvtColor(file, cv.COLOR_BGR2GRAY)
plt.imshow(gray)
plt.show()
print(reader.readtext(gray,detail=0))



cv.waitKey(0)


