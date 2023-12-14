#!/usr/bin/env python3
import wget
import os
import pathlib
TRBOT_PATH=pathlib.Path.home()/".typeracer_bot"
os.makedirs(TRBOT_PATH/"tessdata",exist_ok=True)
wget.download("https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata",str(TRBOT_PATH/"tessdata/eng.traineddata"))
