import requests
from selenium import webdriver
import pyautogui
from PIL import Image
import time
import cv2
from io import BytesIO
import numpy as np

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def find_LoL_subimage(subimage, webpage_ss):

    method = cv2.TM_SQDIFF_NORMED

    # Read the images from the file
    small_image = cv2.imread(subimage)
    large_image = cv2.imread(webpage_ss)

    result = cv2.matchTemplate(small_image, large_image, method)

    # We want the minimum squared difference
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    # Draw the rectangle:
    # Extract the coordinates of our best match
    MPx,MPy = mnLoc

    return MPx, MPy

# we're going to have to sleep a decent bit because the js animations have to phase out of the image before we ss.
driver = webdriver.Chrome(executable_path='../drivers/chromedriver.exe')
width, height = 1024,1024
adj_pix  = 105
crop_tup = (0, height*0.3, width, height)
driver.set_window_position(0,0)
driver.set_window_size(width, height)

# load webpage and handle the continue screen.
driver.get('https://app.prizepicks.com/')
time.sleep(1)
pyautogui.moveTo(width*0.5, height*0.79)
pyautogui.click()

time.sleep(1)
# take screenshot of page, and then locate the LoL tab.
driver.save_screenshot('../images/initial_webpage.png')
x_LoL_i, y_LoL_i = find_LoL_subimage(subimage='../images/LoL.PNG', webpage_ss='../images/initial_webpage.png')
print(x_LoL_i, y_LoL_i)
# navigate to the LoL page.
pyautogui.moveTo(x_LoL_i, y_LoL_i+adj_pix)
time.sleep(10)
pyautogui.click()
time.sleep(1)

# secure initial screenshot
png = driver.get_screenshot_as_png()
img = Image.open(BytesIO(png))
img = img.crop(crop_tup)
img.save('../images/initial_cropped.png')
# screenshot = Image.open('../images/current_state.png')

count = 0
while True:
    try:
        time.sleep(10)
        driver.refresh()
        time.sleep(2)
        driver.save_screenshot('../images/current_state.png')
        x_LoL_c, y_LoL_c = find_LoL_subimage(subimage='../images/LoL.PNG', webpage_ss='../images/current_state.png')
        pyautogui.moveTo(x_LoL_i, y_LoL_i+adj_pix)
        time.sleep(1)
        pyautogui.click()
        ss = f'../images/current_LoL.png'
        driver.save_screenshot(ss)
        screenshot = Image.open(ss)
        im = screenshot.crop(crop_tup)
        im.save('../images/cropped.png')

        a = cv2.imread('../images/initial_cropped.png')
        b = cv2.imread(f'../images/cropped.png')

        diff = cv2.subtract(a,b)
        res = not np.any(diff)
        if res:
            print("pictures are the same.")
        else:
            cv2.imwrite("../images/diff.png", diff )
            print('differences stored in diff.png')

        count += 1
    except KeyboardInterrupt:
        driver.close()
