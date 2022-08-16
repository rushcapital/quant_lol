import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
from PIL import Image
import time
import cv2
from io import BytesIO
import numpy as np

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

    return MPx, MPy, mn

# we're going to have to sleep a decent bit because the js animations have to phase out of the image before we ss.
# Specify all of our formatting

# if we run in headless mode we have to verify we're human.

def check_webpage_for_league_odds(user_agent):

    options = Options()
    # options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--start-fullscreen')

    driver = webdriver.Chrome(executable_path='../drivers/chromedriver.exe', options=options)

    width, height = 1024,1024
    adj_pix  = 105
    crop_tup = (0, height*0.3, width, height)
    driver.set_window_position(0,0)
    driver.set_window_size(width, height)

    # load webpage and handle the continue screen.
    driver.get('https://app.prizepicks.com/')
    driver.save_screenshot('../images/initial_webpage.png')
    
    time.sleep(5)
    # flag to know if the LoL tag is there or not.
    status_flag = True    
    while True:

    # while True:
    #     if page_state == 'complete':
    #         # take screenshot of page, and then locate the LoL tab.
    #         driver.save_screenshot('../images/initial_webpage.png')
    #         x_LoL_i, y_LoL_i, error = find_LoL_subimage(subimage='../images/LoL.PNG', webpage_ss='../images/initial_webpage.png')
    #         print(x_LoL_i, y_LoL_i, error)
    #         if error < 1e-5:
    #             print('LoL lines available.')
    #         else:
    #             print('LoL not present.')
    #         break

    #     else:
    #         pass

if __name__ == '__main__':

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    check_webpage_for_league_odds(user_agent)

# print(page_state)
# time.sleep(5)
# # take screenshot of page, and then locate the LoL tab.
# driver.save_screenshot('../images/initial_webpage.png')
# x_LoL_i, y_LoL_i = find_LoL_subimage(subimage='../images/LoL.PNG', webpage_ss='../images/initial_webpage.png')
# print(x_LoL_i, y_LoL_i)
# # navigate to the LoL page.
# pyautogui.moveTo(x_LoL_i, y_LoL_i)
# time.sleep(10)
# pyautogui.click()
# time.sleep(1)

# # secure initial screenshot
# png = driver.get_screenshot_as_png()
# img = Image.open(BytesIO(png))
# img = img.crop(crop_tup)
# img.save('../images/initial_cropped.png')
# # screenshot = Image.open('../images/current_state.png')

# count = 0
# while True:
#     try:
#         time.sleep(10)
#         driver.refresh()
#         time.sleep(2)
#         driver.save_screenshot('../images/current_state.png')
#         x_LoL_c, y_LoL_c = find_LoL_subimage(subimage='../images/LoL.PNG', webpage_ss='../images/current_state.png')
#         pyautogui.moveTo(x_LoL_i, y_LoL_i)
#         time.sleep(1)
#         pyautogui.click()
#         ss = f'../images/current_LoL.png'
#         driver.save_screenshot(ss)
#         screenshot = Image.open(ss)
#         im = screenshot.crop(crop_tup)
#         im.save('../images/cropped.png')

#         a = cv2.imread('../images/initial_cropped.png')
#         b = cv2.imread(f'../images/cropped.png')

#         diff = cv2.subtract(a,b)
#         res = not np.any(diff)
#         if res:
#             print("pictures are the same.")
#         else:
#             cv2.imwrite("../images/diff.png", diff )
#             print('differences stored in diff.png')

#         count += 1
#     except KeyboardInterrupt:
#         driver.close()
