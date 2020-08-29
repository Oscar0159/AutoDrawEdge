import cv2
import numpy as np

import os
import time
import ctypes
from glob import glob


# 筆畫粗細
LINE_WEIGHT = 5

# 降噪等級
# 過大會導致線條遺失
DENOISE_LEVEL = 6

# 視窗位置
X1, Y1 = 760, 310
X2, Y2 = 1520, 730

# 每 S 秒傳送 N 個滑鼠點擊事件
# 傳送過多可能會導致事件過多而錯誤
S = 1
N = 200


def cv_imread(filename):
    img = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), 0)
    return img


def mouse_click(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left down
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left up


def isBlack(pixel):
    return pixel.tolist() == [0, 0, 0, 255]


def draw(img):
    print('開始繪製-->')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    h, w = img.shape[0:2]
    count = 0
    for i in range(h):
        for j in range(w):
            if i % 2 == 0 and j % 2 == 0:
                if isBlack(img[i][j]):
                    count += 1
                    mouse_click(X1 + j, Y1 + i)
                    if count == N:
                        count = 0
                        time.sleep(S)
    print('滑鼠點擊事件全數傳送完畢')
    print('如有繪製錯誤請降低傳送事件速率')
    print('------------------------------')


def edge(img):
    img = cv2.blur(img, (2, 2))
    img_edge = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                     blockSize=LINE_WEIGHT, C=DENOISE_LEVEL)
    return img_edge


def resize(filename):
    x, y = X2-X1, Y2-Y1
    min_side = y if x > y else x
    img = cv_imread(filename)
    h, w = img.shape[0:2]

    scale = max(w, h) / float(min_side)
    new_w, new_h = int(w / scale), int(h / scale)
    resize_img = cv2.resize(img, (new_w, new_h))

    if new_w % 2 != 0 and new_h % 2 == 0:
        top, bottom, left, right = int((y - new_h) / 2), int((y - new_h) / 2), \
                                   int((x - new_w) / 2 + 1), int((x - new_w) / 2)
    elif new_h % 2 != 0 and new_w % 2 == 0:
        top, bottom, left, right = int((y - new_h) / 2 + 1), int((y - new_h) / 2),\
                                   int((x - new_w) / 2), int((x - new_w) / 2)
    elif new_h % 2 == 0 and new_w % 2 == 0:
        top, bottom, left, right = int((y - new_h) / 2), int((y - new_h) / 2),\
                                   int((x - new_w) / 2), int((x - new_w) / 2)
    else:
        top, bottom, left, right = int((y - new_h) / 2 + 1), int((y - new_h) / 2),\
                                   int((x - new_w) / 2 + 1), int((x - new_w) / 2)

    pad_img = cv2.copyMakeBorder(resize_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    return pad_img


if __name__ == "__main__":
    if not os.path.exists('images'):
        os.makedirs('images')

    types = ('*.jpg', '*.png')  # the tuple of file types
    file_list = []
    for files in types:
        file_list.extend(glob('images/' + files))

    for filename in file_list:
        draw(edge(resize(filename)))
