from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from playsound import playsound
import os
import time
import threading
from OCR import prepare_ocr
from Neural_Network_Predict import image_analyzer
import tensorflow as tf
from Golfer_List import get_active_golfer_list
import keyboard
from tensorflow.keras import datasets, layers, models, optimizers, callbacks

def keyboard_monitoring(driver):
    while True:
        try:
            #Checks to see if video is paused
            paused = driver.execute_script('return document.getElementsByTagName("video")[0].paused')
            if keyboard.is_pressed("P") and paused:
                driver.execute_script('document.getElementsByTagName("video")[0].play()')
                driver.execute_script('document.getElementsByTagName("video")[0].playbackRate=1')
            elif keyboard.is_pressed("P") and not paused:
                driver.execute_script('document.getElementsByTagName("video")[0].pause()')
            elif keyboard.is_pressed("S"):
                driver.execute_script('document.getElementsByTagName("video")[0].play()')
                driver.execute_script('document.getElementsByTagName("video")[0].playbackRate=5')
            elif keyboard.is_pressed("R"):
                driver.execute_script('document.getElementsByTagName("video")[0].play()')
                driver.execute_script('document.getElementsByTagName("video")[0].playbackRate=-1')
            # time.sleep(0.25)
        except:
            continue


os.chdir(r"C:\Users\manag\Documents\GitHub\AIoftheTiger")
f = open("directory.txt", "r")
path = f.read()

# defines the model we use for our Neural Network
my_model = path + "RE-test-model-030.h5"
reconstructed_model = tf.keras.models.load_model(my_model)

# gets all our tools to run the OCR
creds, drive_service, doc_service = prepare_ocr()

url = input("What url do you want me to watch? ")
done = False
golfer_list = []
active_golfers = get_active_golfer_list(path + "default_golfer_list.txt")

while done == False:
    golfer = input("Input the last name of a golfer you would like to watch. "
                   "Input '0' when you have listed all golfers you want to watch: ")
    if golfer != '0':
        # check if golfer is in active golfer list
        golfer = golfer.upper() + '\n'
        if golfer in active_golfers:
            golfer_list.append(golfer[:-1])
        else:
            overwrite = input("WARNING! The golfer you entered doesn't exist in our list. Do you still want"
                              "to continue? Enter 'y' to use your golfer.")
            overwrite = overwrite.upper()
            if overwrite == 'Y':
                golfer_list.append(golfer)
            else:
                continue
    elif len(golfer_list) == 0:
        print("Please enter the name of at least one golfer.")
        continue
    else:
        done = True

# url = "https://www.youtube.com/watch?v=-dlgPrBYcuY"
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)
# driver.maximize_window()
driver.fullscreen_window()

# control_thread = threading.Thread(target=keyboard_monitoring, args=([driver]))
# control_thread.start()
# # print(driver)
# print(control_thread.is_alive())

fileName = "screenshot.jpg"
stop_token = True
lag_time = 0
# paused = False

while True:
    # time.sleep(5)
    driver.get_screenshot_as_file(fileName)
    try:
        result = image_analyzer(path + fileName, reconstructed_model, stop_token, creds, golfer_list, drive_service,
                                doc_service, driver)
    except Exception as e:
        print(str(e))
    # os.system('cls')
    print(result[1], lag_time)
    stop_token = result[2]
    start_time = result[3]
    if result[0]:
        playsound('glf+swng.mp3')
        paused = True
        lag_addition = 0
        while paused:
            paused = driver.execute_script('return document.getElementsByTagName("video")[0].paused')
            if keyboard.is_pressed("P") and lag_addition == 0:
                driver.execute_script('document.getElementsByTagName("video")[0].play()')
                end_time = time.time()
                lag_time = end_time - start_time
                lag_addition = 1
        while keyboard.is_pressed("D") != True:
            continue
        # time.sleep(10)
    elif result[1] == 5:
        driver.execute_script('document.getElementsByTagName("video")[0].play()')
        end_time = time.time()
        lag_time += end_time - start_time

    paused = driver.execute_script('return document.getElementsByTagName("video")[0].paused')
    if lag_time >= 0.5 and not paused:
        current_time = time.time()
        end_time = time.time() + 0.5
        driver.execute_script('document.getElementsByTagName("video")[0].playbackRate=2')
        while current_time <= end_time:
            current_time = time.time()
        driver.execute_script('document.getElementsByTagName("video")[0].playbackRate=1')
        lag_time -= 0.5