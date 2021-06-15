import cv2
import pytesseract
import sys

img = cv2.imread('boleta_frog2.jpg')

if img is None:
    sys.exit("Could not read the image.")

h, w, c = img.shape

e1 = cv2.getTickCount

boxes = pytesseract.image_to_boxes(img) 
for b in boxes.splitlines():
    b = b.split(' ')
    img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)

e2 = cv2.getTickCount()
time = (e2 - e1)/ cv2.getTickFrequency()

print (time)

cv2.namedWindow("output", cv2.WINDOW_NORMAL)
cv2.imshow('output', img)
cv2.waitKey(0)