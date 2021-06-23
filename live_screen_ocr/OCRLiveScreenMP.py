import time
import re
import cv2
import json
import numpy as np
import pytesseract
import threading

from helper import frame_generator, show_image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def save_json(file_name, data):
    with open(file_name, 'w') as f:
        f.write(json.dumps(data, indent=2))
    f.close()


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
        self.Masks = {"green": self._GreenMask, "red": self._RedMask, "white": self._WhiteMask}
        self.FinalDict = {}

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
            # if self.Counter > 75:
            #     break
            self.Counter += 1
            screen = self._GetCurrentFrame()
            # if self.Counter < 25:
            #     continue
            start_time = time.time()
            results = self._SplitImage(screen)
            final_dict = self._GetFinalDict(results['green'], results['red'], results['white'])
            # if len(final_dict) == 0:
            #     cv2.imwrite(f'{self.Counter}.png', screen)
            #     save_json(f'{self.Counter}.json', results)

            diff = round(time.time() - start_time, 4)
            total_time += diff
            print(self.Counter, '--->', final_dict)
            # show_image(screen, 'Optimized')
            # print(f"-> Count: {self.Counter} Took Time: {diff} sec {final_dict}\n")

        print("\nTotal Time: ", total_time)

    def _GetMaskedValues(self, image_data, mask_key, results):
        mask_params = self.Masks[mask_key]
        mask = cv2.inRange(self.HSV, *mask_params)
        imask = mask > 0
        white = np.zeros_like(image_data, np.uint8)
        white[imask] = image_data[imask]
        white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(white, lang='eng', config='digits')
        results[mask_key] = re.findall("\d+\.\d+", text)

    def _AssignValues(self, values):
        final_dict = {}
        for data in values:
            color = data['color']
            array = data['array']

            if color == "red":
                final_dict['i'] = array[0]
                final_dict['j'] = array[1]
                final_dict['k'] = array[2]
                final_dict['l'] = array[3]
                final_dict['m'] = array[4]
                final_dict['n'] = array[5]
                final_dict['o'] = array[6]
                final_dict['p'] = array[7]

            elif color == "green":
                final_dict['a'] = array[0]
                final_dict['b'] = array[1]
                final_dict['c'] = array[2]
                final_dict['d'] = array[3]
                final_dict['e'] = array[4]
                final_dict['f'] = array[5]
                final_dict['g'] = array[6]
                final_dict['h'] = array[7]

            elif color == "white":
                final_dict['q'] = array[0]
                final_dict['r'] = array[1]
                final_dict['s'] = array[2]
                final_dict['t'] = array[3]
                final_dict['u'] = array[4]
                final_dict['v'] = array[5]
                final_dict['w'] = array[6]
                final_dict['x'] = array[7]
        return final_dict

    def _GetFinalDict(self, green_numbers, red_numbers, white_numbers):
        final_dict = {}
        if len(red_numbers) == 8 and len(green_numbers) == 8 and len(white_numbers) == 8:

            values = [{'color': "red", "array": red_numbers}, {'color': "green", "array": green_numbers},
                      {'color': "white", "array": white_numbers}]
            final_dict = self._AssignValues(values)

        elif len(red_numbers) == 8 or len(green_numbers) == 8 or len(white_numbers) == 8:
            if len(red_numbers) == 8:
                final_dict.update(self._AssignValues([{'color': "red", "array": red_numbers}]))

            if len(green_numbers) == 8:
                final_dict.update(self._AssignValues([{'color': "green", "array": green_numbers}]))

            if len(white_numbers) == 8:
                final_dict.update(self._AssignValues([{'color': "white", "array": white_numbers}]))

        return final_dict

    def _SplitImage(self, image_data):
        # convert to hsv
        self.HSV = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        # mask of green (36,25,25) ~ (86, 255,255)

        threads = []
        keys = list(self.Masks.keys())
        results = {}
        for i in range(3):
            t = threading.Thread(target=self._GetMaskedValues, args=(image_data, keys[i], results))
            threads.append(t)
            t.start()

        for th in threads:
            th.join()

        # print("Green: ", results['green'])
        # print("Red: ", results['red'])
        # print("White: ", results['white'])
        self._Reset()
        return results


live_ocr = OCRLiveScreen()
live_ocr.Start()