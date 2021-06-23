import time
import re
import cv2
import numpy as np
import pytesseract
from helper import frame_generator, show_image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCRLiveScreen:
    def __init__(self):
        self.RedImage = None
        self.GreenImage = None
        self.WhiteImage = None
        self.HSV = None
        self.FrameGenerator = frame_generator('video.mkv')
        self.Counter = 0
        self._GreenMask = (54, 90, 71), (100, 255, 255)
        self._RedMask = (130, 130, 130), (179, 255, 255)
        self._WhiteMask = (0, 0, 204), (173, 255, 255)

    def _Reset(self):
        self.RedImage = None
        self.GreenImage = None
        self.WhiteImage = None
        self.HSV = None

    def _GetCurrentFrame(self):
        screen = next(self.FrameGenerator)
        return screen

    def Start(self):
        total_time = 0
        while True:
            if self.Counter > 75:
                break
            self.Counter += 1
            screen = self._GetCurrentFrame()
            if self.Counter < 25:
                continue
            start_time = time.time()
            self._SplitImage(screen)
            diff = round(time.time() - start_time, 4)
            total_time += diff
            print(f"------- Count: {self.Counter} Took Time: {diff} sec\n")

        print("\nTotal Time: ", total_time)

    def _GetGreenMaskedValues(self, image_data):
        mask = cv2.inRange(self.HSV, *self._GreenMask)
        imask = mask > 0
        green = np.zeros_like(image_data, np.uint8)
        green[imask] = image_data[imask]
        green = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(green, lang='eng', config='digits')
        return re.findall("\d+\.\d+", text)

    def _GetRedMaskedValues(self, image_data):
        mask = cv2.inRange(self.HSV, *self._RedMask)
        imask = mask > 0
        red = np.zeros_like(image_data, np.uint8)
        red[imask] = image_data[imask]
        red = cv2.cvtColor(red, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(red, lang='eng', config='digits')
        return re.findall("\d+\.\d+", text)

    def _GetWhiteMaskedValues(self, image_data):
        mask = cv2.inRange(self.HSV, *self._WhiteMask)
        imask = mask > 0
        white = np.zeros_like(image_data, np.uint8)
        white[imask] = image_data[imask]
        white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(white, lang='eng', config='digits')
        return re.findall("\d+\.\d+", text)

    def _SplitImage(self, image_data):
        # convert to hsv
        self.HSV = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        # mask of green (36,25,25) ~ (86, 255,255)
        green_txt = self._GetGreenMaskedValues(image_data)
        red_txt = self._GetRedMaskedValues(image_data)
        white_txt = self._GetWhiteMaskedValues(image_data)
        print("Green: ", green_txt)
        print("Red: ", red_txt)
        print("White: ", white_txt)
        self._Reset()


live_ocr = OCRLiveScreen()
live_ocr.Start()