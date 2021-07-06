import cv2
black = [0,0,0]
img1 = cv2.imread('geant_L.tif')
constant= cv2.copyMakeBorder(img1,200,200,200,200,cv2.BORDER_CONSTANT,value=black)
cv2.imwrite('geant_L1.jpg',constant)
