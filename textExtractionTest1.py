# https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/

import cv2
import time
import numpy
import pytesseract


def outputConsoleText(text):
    if type(text) is list:
        1+1
    elif(text.startswith("TIMER: ")):
        print(text)


QUIT_KEY = "q"
RESET_KEY = "r"
# NEWFACE_TIMEOUT = 5

VIDEO_STREAM_RTSP_GLOBAL = ["rtsp://___.___.___:####/_", True, 1]
VIDEO_STREAM_RTSP_LOCAL = ["rtsp://192.168.1.#:####/_", True, 0]
VIDEO_STREAM_INTERNET = ["rtsp://___.___.___", True, 0]
VIDEO_STREAM_WEBCAM = [0, True, 0]
STATIC_INTERNET_IMAGE = ["https://_._.com/_.png", True, 0]
STATIC_INTERNET_IMAGE_42 = ["https://ia800701.us.archive.org/BookReader/BookReaderImages.php?zip=/18/items/TheultimateHitchhikersGuide/The Hitchhiker's Guide To The Galaxy_jp2.zip&file=The Hitchhiker's Guide To The Galaxy_jp2/The Hitchhiker's Guide To The Galaxy_0009.jp2&id=TheultimateHitchhikersGuide", True, 0]
STATIC_LOCAL_IMAGE_42 = ["42.png", False, 4]

VIDEO_STREAM = STATIC_LOCAL_IMAGE_42


if VIDEO_STREAM == STATIC_LOCAL_IMAGE_42:
    tmp = cv2.VideoCapture(STATIC_INTERNET_IMAGE_42[0])
    tmp, tmp = tmp.read()
    cv2.imwrite('42.png', tmp)

cap = 0  # cv2.VideoCapture(VIDEO_STREAM)

# MAPS
originalColorMap = 0
gray = 0
outputMap = 0

awaitingSelect = True

rect = 0
img = 0
thresh1 = 0
rect_kernel = 0
iterations = 0

thisList = []

MAX_SLIDER_VALUE = 100
MS_WAIT_TIME_FRAMES = 300
PAUSE_PER_DETECTED_GREEN_MS = 1
windowName = "Display window"

cv2.namedWindow(windowName)
trackbar_name = 'Kernel Dimensions () %d' % MAX_SLIDER_VALUE

kernel_size_opt1 = 20
kernel_size_opt2 = kernel_size_opt1

textString = ""

tmpTimerValue = -1

outputConsoleText("Stating...")


def on_trackbar_change(val):
    global kernel_size_opt1
    kernel_size_opt1 = val
    global kernel_size_opt2
    kernel_size_opt2 = val


def startTimer():
    global tmpTimerValue
    tmpTimerValue = time.time()
def endTimer(message):
    global tmpTimerValue
    outputConsoleText("TIMER: "+str(message)+" : "+str((time.time()-tmpTimerValue)*1000))

cv2.createTrackbar(trackbar_name, windowName, kernel_size_opt1, MAX_SLIDER_VALUE, on_trackbar_change)

# loop runs if capturing has been initialized.
while 1:

    if awaitingSelect:
        if VIDEO_STREAM[1]:  # If it's a stream vs an image
            cap = cv2.VideoCapture(VIDEO_STREAM[0])
            ret, img = cap.read()
            if VIDEO_STREAM[2] == 1:
                img = cv2.flip(img, VIDEO_STREAM[2])  # Flip the image
        else:
            img = cv2.imread(VIDEO_STREAM[0])
            img = cv2.rotate(img, VIDEO_STREAM[2], img)  # Rotate the image

# MAKE MORE SPACE ABOVE IMAGE SO TEXT DOESN'T BLOCK OUT IMAGE
        # img2 = numpy.zeros((img.shape[0]+100, img.shape[1], 3))
        # img2[100:img.shape[0]+100, 0:img.shape[1]] = img
        img2 = img.copy()
        img2 = cv2.resize(img2, (img2.shape[1], img2.shape[0]))
        img2 = cv2.rectangle(img2, (0, 0), (img2.shape[1], 200), (0, 0, 0), -1)  # Make card take up the entire with
        img2 = cv2.putText(img2, "Looking for: [ "+textString+" ]", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(windowName, img2)



    else:
        numberOfFoundStatements = 0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Performing OTSU threshold
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Specify structure shape and kernel size.
        # Kernel size increases or decreases the area
        # of the rectangle to be detected.
        # A smaller value like (10, 10) will detect
        # each word instead of a sentence.
        startTimer()
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size_opt1, kernel_size_opt2))
        endTimer("rect_kernel")
        # Applying dilation on the threshold image
        iterations = 1

        startTimer()
        dilation = cv2.dilate(thresh1, rect_kernel, iterations)
        endTimer("Dilate")

        # Finding contours
        startTimer()
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_NONE)
        endTimer("Contours")

        # Looping through the identified contours
        # Then rectangular part is cropped and passed on
        # to pytesseract for extracting text from it
        # Extracted text is then written into the text file
        # for cnt in contours:
        startTimer()
        for cnt in reversed(contours):
            x, y, w, h = cv2.boundingRect(cnt)

            # Drawing a rectangle on copied image
            # rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cv2.imshow("",rect)
            cv2.imshow(windowName, img)

            # Cropping the text block for giving input to OCR
            cropped = img[y:y + h, x:x + w]

            # Apply OCR on the cropped image
            text = pytesseract.image_to_string(cropped)
            if len(text.replace(" ", "")) > 0:
                outputConsoleText(">" + text.strip() + "<")
                secondD = []
                secondD.append(text.strip())

                secondD.append(x)
                secondD.append(y)
                secondD.append(w)
                secondD.append(h)
                thisList.append(secondD)

            # Display an image in a window
                if textString.lower() in text:
                    numberOfFoundStatements += 1
                    rect = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255, 100), 5)
                else:
                    rect = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.waitKey(PAUSE_PER_DETECTED_GREEN_MS) & 0xff
        awaitingSelect = True
        outputConsoleText(thisList)
        outputConsoleText("\n")
        endTimer("Contours2")

        arr = []
        for i in range(len(thisList)):
            col = []
            for j in range(len(thisList[i])):
                col.append(thisList[i][j])
            arr.append(col)
        outputConsoleText(arr)

        outputConsoleText("\n")
        # for i in range(len(thisList)):
        #     if textString.lower() in thisList[i][0]:  # and (i != 24):
        #         outputConsoleText(str(i) + " (" + thisList[i][0].replace("\n", "") + ")")
        #         img = cv2.rectangle(img, (thisList[i][1], thisList[i][2]),
        #                             (thisList[i][1] + thisList[i][3], thisList[i][2] + thisList[i][4]), (255, 0, 0), 4)
        #         # img = cv2.rectangle(img, (10, 10), (50, 50), (255, 0, 0), 20)

        img = cv2.rectangle(img, (0, 0), (img.shape[1], 100), (0, 0, 0), -1)  # Make card take up the entire with
        img = cv2.putText(img, "Located "+str(numberOfFoundStatements)+" instances in the text of: [ " + textString + " ]", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 2,
                           (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(windowName, img)
        cv2.waitKey(0)

    # Wait for Esc key to stop
    k = cv2.waitKey(MS_WAIT_TIME_FRAMES) & 0xff
    if k == 27:
        break
    elif k == 13:  # (ENTER KEY) ord(RESET_KEY):
        awaitingSelect = False
    elif k == 127:  # Backspace
        textString = textString[:max(len(textString)-1,0)]
    elif k != ord("ÿ"):
        textString += chr(k)
        outputConsoleText(textString)
    # if k == ord(QUIT_KEY):
    #     break

# Close the window
cap.release()

# De-allocate any associated memory usage
cv2.destroyAllWindows()
