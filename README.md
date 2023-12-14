# TYPERACER-BOT

A simple bot for https://www.typeracer.com/ made for fun.
The account it runs on: https://data.typeracer.com/pit/profile?user=thetyperacerbot

## Setup

Just run
```
python -m pip install -r requirements.txt
python typeracer_setup.py
```

## Running

```
python typeracer_bot.py
```

## How it works

### Normal runtime
`typeracer_bot` uses the [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/) to access TypeRacer.
It looks at the text on the page and types it into the input box.

### Captchas
Captchas on this particular website are quite annoying and difficult to deal with (that is their entire point).
`typeracer_bot` first pre-processes the image by removing the black lines over the captcha, then it solves the captcha using [Tesseract](https://github.com/tesseract-ocr/tesseract). Tesseract reaches an acurracy of about 80%-90% most of the time, so don't expect the captcha to be solved immediately. It may take some time.

## Results

Best so far: 413 WPM without getting banned
![Leaderboard](https://github.com/jenca-adam/typeracer-bot/blob/main/leaderboard.png?raw=true "413 WPM")
