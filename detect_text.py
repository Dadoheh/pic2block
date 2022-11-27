import shapes

import cv2
import pytesseract
from definitions import SAMPLE_TEXT, RESIZED_SHAPES_PNG

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Read image from which text needs to be extracted
img = cv2.imread(SAMPLE_TEXT)
# Preprocessing the image starts
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
cv2.imwrite('threshold_image.jpg', thresh1)

rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
dilation = cv2.dilate(thresh1, rect_kernel, iterations=6)
cv2.imwrite('dilation_image.jpg', dilation)
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
im2 = img.copy()

for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    rect=cv2.rectangle(im2, (x,y), (x+w, y+h), (0,255,0), 2)
    cropped = im2[y:y+h, x:x+w]
    cv2.imwrite('rectanglebox.jpg',rect)
    text = pytesseract.image_to_string(cropped)
    print(f"TEXT: {text}")
