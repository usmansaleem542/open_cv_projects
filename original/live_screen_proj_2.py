from multiprocessing import Process

from PIL import ImageGrab
import pytesseract
import time
import numpy as np
import cv2
import re
from helper import frame_generator, show_image

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def split_img():
    ## convert to hsv
    img = cv2.imread('grabbed.png')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    ## mask of green (36,25,25) ~ (86, 255,255)
    mask = cv2.inRange(hsv, (54, 90, 71), (100, 255, 255))

    ## slice the green
    imask = mask > 0
    green = np.zeros_like(img, np.uint8)
    green[imask] = img[imask]
    cv2.imwrite("green.png", green)
    img123 = cv2.imread("green.png")
    abs = cv2.cvtColor(img123, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("greenbw.png", abs)

    ## slice the red
    mask = cv2.inRange(hsv, (130, 130, 130), (179, 255, 255))
    imask = mask > 0
    red = np.zeros_like(img, np.uint8)
    red[imask] = img[imask]

    ##convert to gray
    cv2.imwrite("red.png", red)
    img123 = cv2.imread("red.png")
    abs = cv2.cvtColor(img123, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("redbw.png", abs)

    ## slice the white
    mask = cv2.inRange(hsv, (0, 0, 204), (173, 255, 255))
    imask = mask > 0
    white = np.zeros_like(img, np.uint8)
    white[imask] = img[imask]

    ## save
    cv2.imwrite("white.png", white)

def split_img_in_memory(img):
    ## convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    ## mask of green (36,25,25) ~ (86, 255,255)
    mask = cv2.inRange(hsv, (54, 90, 71), (100, 255, 255))

    ## slice the green
    imask = mask > 0
    green = np.zeros_like(img, np.uint8)
    green[imask] = img[imask]
    # yield green

    img123 = green.copy()

    abs = cv2.cvtColor(img123, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("greenbw.png", abs)

    ## slice the red
    mask = cv2.inRange(hsv, (130, 130, 130), (179, 255, 255))
    imask = mask > 0
    red = np.zeros_like(img, np.uint8)
    red[imask] = img[imask]

    ##convert to gray
    # cv2.imwrite("red.png", red)
    img123 = red.copy()
    abs = cv2.cvtColor(img123, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("redbw.png", abs)

    ## slice the white
    mask = cv2.inRange(hsv, (0, 0, 204), (173, 255, 255))
    imask = mask > 0
    white = np.zeros_like(img, np.uint8)
    white[imask] = img[imask]

    ## save
    cv2.imwrite("white.png", white)

    return green, white, abs


def get_num_list(image):
    height, width, channels = image.shape
    croppedImage = image[int(height / 6):height, 0:width]
    cropped = croppedImage

    num_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", ","]
    list = []
    text = pytesseract.image_to_string(cropped)

    text = re.split('\n|\s', text)
    for words in text:
        value = True
        for i in str(words):
            if (i in num_list) and (value == True):
                pass
            elif i == "":
                value = False
            else:
                value = False
        if value == True:
            if (words != "") and ("." in words or "," in words) and (len(words) >= 3):
                list.append(words)

    return list


def get_num_list_in_memory(image):
    height = image.shape[0]
    width = image.shape[1]
    croppedImage = image[int(height / 6):height, 0:width]
    cropped = croppedImage

    num_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", ","]
    list = []
    text = pytesseract.image_to_string(cropped)

    text = re.split('\n|\s', text)
    for words in text:
        value = True
        for i in str(words):
            if (i in num_list) and (value == True):
                pass
            elif i == "":
                value = False
            else:
                value = False
        if value == True:
            if (words != "") and ("." in words or "," in words) and (len(words) >= 3):
                list.append(words)

    return list


def assign_values(values):
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


def get_values():
    final_dict = {}
    img_gen = frame_generator()
    frame = 0
    total_time = 0
    while True:
        frame += 1
        if frame >= 50:
            break
        # get screen shot
        # screen = ImageGrab.grab()
        # screen.save('grabbed.png')
        start_time = time.time()
        screen = next(img_gen)
        cv2.imwrite("grabbed.png", screen)

        #split screen shot by color
        split_img()

        green_image = cv2.imread('greenbw.png')
        white_image = cv2.imread('white.png')
        red_image = cv2.imread('redbw.png')

        #read image text and get numbers list
        green_numbers = get_num_list(green_image)
        white_numbers = get_num_list(white_image)
        red_numbers = get_num_list(red_image)

        if len(red_numbers) == 8 and len(green_numbers) == 8 and len(white_numbers) == 8:

            values = [{'color': "red", "array": red_numbers}, {'color': "green", "array": green_numbers},
                      {'color': "white", "array": white_numbers}]
            final_dict = assign_values(values)

        elif len(red_numbers) == 8 or len(green_numbers) == 8 or len(white_numbers) == 8:
            if len(red_numbers) == 8:
                final_dict.update(assign_values([{'color': "red", "array": red_numbers}]))

            if len(green_numbers) == 8:
                final_dict.update(assign_values([{'color': "green", "array": green_numbers}]))

            if len(white_numbers) == 8:
                final_dict.update(assign_values([{'color': "white", "array": white_numbers}]))
        time_taken = round(time.time() - start_time, 4)
        total_time += time_taken
        # print(time_taken, "-->", final_dict)
        print("Frame: ", frame, "--> {} sec".format(time_taken))

    print("Total Time: ", total_time)
        # time.sleep(0.0001)


def get_values_in_memory():
    final_dict = {}
    img_gen = frame_generator()
    frame = 0
    total_time = 0
    while True:
        frame += 1
        if frame >= 50:
            break
        # get screen shot
        # screen = ImageGrab.grab()
        # screen.save('grabbed.png')
        start_time = time.time()
        screen = next(img_gen)
        # cv2.imwrite("grabbed.png", screen)

        #split screen shot by color
        green_image, white_image, red_image = split_img_in_memory(screen)
        # show_image(green_image)
        # show_image(white_image)
        # show_image(red_image)
        # green_image = cv2.imread('greenbw.png')
        # white_image = cv2.imread('white.png')
        # red_image = cv2.imread('redbw.png')

        #read image text and get numbers list
        green_numbers = get_num_list_in_memory(green_image)
        white_numbers = get_num_list_in_memory(white_image)
        red_numbers = get_num_list_in_memory(red_image)

        if len(red_numbers) == 8 and len(green_numbers) == 8 and len(white_numbers) == 8:

            values = [{'color': "red", "array": red_numbers}, {'color': "green", "array": green_numbers},
                      {'color': "white", "array": white_numbers}]
            final_dict = assign_values(values)

        elif len(red_numbers) == 8 or len(green_numbers) == 8 or len(white_numbers) == 8:
            if len(red_numbers) == 8:
                final_dict.update(assign_values([{'color': "red", "array": red_numbers}]))

            if len(green_numbers) == 8:
                final_dict.update(assign_values([{'color': "green", "array": green_numbers}]))

            if len(white_numbers) == 8:
                final_dict.update(assign_values([{'color': "white", "array": white_numbers}]))
        time_taken = round(time.time() - start_time, 4)
        total_time += time_taken
        # print(time_taken, "-->", final_dict)
        print("Frame: ", frame, "--> {} sec".format(time_taken), final_dict)

    print("Total Time: ", total_time)
        # time.sleep(0.0001)


# def frame_generator():
#     cap = cv2.VideoCapture('video.mkv')
#     # Get the frames per second
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     # Get the total numer of frames in the video.
#     frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
#
#     # Calculate the duration of the video in seconds
#     duration = frame_count / fps
#
#     second = 0
#     cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # optional
#     success, image = cap.read()
#
#     while success and second <= duration:
#         # do stuff
#
#         second += 1
#         cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
#         success, image = cap.read()
#         yield image
#
#
# def show_image(img):
#     cv2.imshow('dst_rt', img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()


def test_generator():
    gen = frame_generator()
    for i in range(20):
        show_image(next(gen))

if __name__ == "__main__":
    # test_generator()
    # get_values()
    get_values_in_memory()