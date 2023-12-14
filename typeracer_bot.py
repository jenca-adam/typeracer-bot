#!/usr/bin/env python3
#### BEGIN SETUP BLOCK
import os
import pathlib
if os.environ.get("TESSDATA_PREFIX")!=pathlib.Path.home()/".typeracer_bot/tessdata":
    print("setting the tesseract data directory")
    os.environ["TESSDATA_PREFIX"]=str(pathlib.Path.home()/".typeracer_bot/tessdata")
#### END SETUP BLOCK
import selenium.webdriver,time
import getkey
import sys
import getpass
import random
import pytesseract
from PIL import Image
from io import BytesIO
import cv2 
import numpy as np
import tempfile
from difflib import get_close_matches
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.firefox.options import Options as FFoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
black_lo=np.array([0,0,0])
black_hi=np.array([255,255,70])
def create_driver(headless=False):
    try:# preferably use firefox because fuck chrome
        opt=FFoxOptions()
        if headless:
            opt.add_argument("--headless")
        driver=selenium.webdriver.Firefox(options=opt)
    except:
        opt=ChromeOptions
        if headless:
            opt.add_argument("--headless")
        driver=selenium.webdriver.Chrome(options=opt)
    return driver
def ask_key(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    k=getkey.getkey()
    print()
    return k
def ocr_preprocess(img):
    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 2
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,black_lo,black_hi)
    SE   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask = cv2.dilate(mask, SE, iterations=1)
    img[mask>0]=dominant
    return img
if __name__=="__main__":
    always=False
    wpm=float(input("Target WPM:"))
    charbychar=ask_key("Character-by-character mode? [y*]") in "y"
    if charbychar:
        key=ask_key("Bypass bot protection(humanify)? (WPM won't be as high)[y*]")
        bypass = key.lower() in "y"
    key=ask_key("Log in?[y*]")
    log_in = key.lower() in "y"
    if log_in:
        username = input("Username:")
        password = getpass.getpass("Password:")
    else:
        username=password=None
    key=ask_key("Headless mode?[y*]")
    if key.lower() in "y":
        headless=True
    else:
        headless=False
    print("\nStarting the Web Driver")
    x=create_driver(headless)
    x.get('https://play.typeracer.com')
    time.sleep(3.1)
    x.find_element(By.XPATH,'//*[contains(text(),\'AGREE\')]').click()

    if log_in:
        print("Logging in")
        x.find_element('css selector','a.promptBtn.signIn').click()
        x.find_element(By.XPATH,'//input[@name="username"]').send_keys(username)
        x.find_element(By.XPATH,'//input[@name="password"]').send_keys(password)
        x.find_element(By.XPATH,'//button[contains(text(),"Sign In")]').click()
        time.sleep(1)
        try:
            al=Alert(x)
            if al.text:
                print(al.text)
                al.accept()
                x.close()
                exit(1)
        except:
            pass
        try:
            x.find_element(By.XPATH,'//div[@title="close this popup"]').click()
        except:pass
        print("login successful")
    print("Entering a race")
    x.find_element(By.XPATH,'//*[contains(text(),\'Enter a Typing Race\')]').click()
    while True:
        dq=False
        time.sleep(1)
        inp=x.find_element("tag name","input")
        seen_countdown=False
        while True:
            try:
                a=x.find_element(By.XPATH,'/html/body/div[5]/div/table/tbody/tr/td/table/tbody/tr/td[3]/div/span')
                if a.text==":00":
                    break
                if a.text.startswith(":0"):
                    print("\rCountdown:",a.text,end="")
                    seen_countdown=True
            except:
                if seen_countdown:
                    break
        print("\ntyping")
        time.sleep(.7)
        def _mkpos(a):
            if a>=0:
                return a
            return 0
        t = x.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div/div[1]/div[1]/table/tbody/tr[2]/td[2]/div/div[1]/div/table/tbody/tr[2]/td[3]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]').text
        total_sleep_time=60*(1/wpm)
        sleep_time_per_char = total_sleep_time*len(t.split())/len(t)
        for i in t.split():
            try:
                i+=" "
                if charbychar:
                    for q in i:
                        sys.stdout.write(q)
                        sys.stdout.flush()
                        try:
                            inp.send_keys(q) # send one char
                        except:
                            break
                        if bypass:
                            time.sleep(_mkpos(sleep_time_per_char+random.randrange(-20,20)/100))
                        else:
                            time.sleep(sleep_time_per_char)
                else:
                    inp.send_keys(i)
                    sys.stdout.write(i)
                    sys.stdout.flush()
                    time.sleep(total_sleep_time)
            except UnexpectedAlertPresentException:
                dq=True
                print("Disqualified!")
                try:
                    al=x.switch_to.alert
                    al.accept()
                except:
                    pass
            except:
                pass
        time.sleep(3)#wait for alerts
        try:
            al=x.switch_to.alert
            if al.text:
                dq=True
                print("Disqualified!")
                al.accept()
        except:pass
        try:
            if x.find_element("css selector",".DialogBox").is_displayed():
                print(x.find_element("css selector",".DialogBox").text)
                if "disqualified" in x.find_element("css selector","div.DialogBox").text :
                    print("Disqualified!")
                    dq=True
                    x.find_element("css selector",".gwt-Button").click()
                elif "typing test" in x.find_element("css selector","div.DialogBox").text:
                    print("Captcha triggered")
                    time.sleep(.2)
                    while True: 
                        x.find_element("css selector",".gwt-Button").click()
                        time.sleep(2)
                        print("Solving...")
                        image=x.find_element("css selector",".challengeImg").screenshot_as_png
                        captcha_temp_file=tempfile.NamedTemporaryFile(prefix="captcha",suffix=".png")
                        captcha_temp_file.file.write(image)
                        cvim = cv2.imread(captcha_temp_file.name)
                        cvim = ocr_preprocess(cvim)
                        solution=pytesseract.image_to_string(cvim)
                        print("Solution: ",repr(solution))

                        x.find_element("css selector",".challengeTextArea").send_keys(solution)
                        x.find_element("css selector",".gwt-Button").click()
                        time.sleep(1)
                        q=x.find_element("css selector","div.DialogBox").text
                        if "Sorry" not in q:
                            print("Captcha passed!")
                            break
                        elif "no more retry" in q:
                            print("Captcha failed with no retries!")
                            break
                        print("Captcha failed, retrying.")
                    x.find_element(By.XPATH,'//div[@title="close this popup"]').click()
        except:pass
        print("\nRace finished.")
        try:
            print("real WPM =>", x.find_element("css selector","div.rankPanelWpm.rankPanelWpm-self").text.split()[0],"target=>",wpm)
        except:
            print("real WPM => ???, target=>",wpm)
        if not dq:
            print("place:",x.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div/div[1]/div[1]/table/tbody/tr[2]/td[2]/div/div[1]/div/table/tbody/tr[2]/td[3]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/div/div/div/table[1]/tbody/tr/td[2]/div/div[1]').text[0])
        else:
            print("place: DQ")
        if not always:
            q=ask_key("Race again?[y (yes) n (no) a (always)]")
            if q=="n":
                break
            always = q=="a"
        print("racing again")
        try:
            x.find_element("css selector","a.raceAgainLink").click()
        except:
            pass
    x.close()
