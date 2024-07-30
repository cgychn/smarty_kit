import time

import requests
import os
import json

headers = {'content-type': 'application/json'}


def test_audio(audio_path):
    req = {
        "audio": audio_path,
        "audio_format": "wav",
        "sample_rate": 16000,
        "lang": "zh_cn",
    }
    r = requests.post("http://127.0.0.1:8099/paddlespeech/asr", data=json.dumps(req), headers=headers)
    print(r.text)


def test_ocr(image_path):
    req = {
        "image": image_path,
        "cls": False
    }
    r = requests.post("http://127.0.0.1:8099/paddleocr", data=json.dumps(req), headers=headers)
    print(r.text)


def test_vector(audio_path):
    req = {
        "audio_file": audio_path
    }
    r = requests.post("http://127.0.0.1:8099/paddlespeech/vector", data=json.dumps(req), headers=headers)
    print(r.text)


def test_translate(text):
    req = {
        "text": text,
        "from_lang": "English",
        "to_lang": "Chinese"
    }
    r = requests.post("http://127.0.0.1:8099/translate", data=json.dumps(req), headers=headers)
    print(r.text + "\n")

proverbs = [
    "All good things must come to an end.",
    "Beauty is in the eye of the beholder.",
    "Better late than never.",
    "Don't bite the hand that feeds you.",
    "Don't count your chickens before they hatch.",
    "Don't cry over spilled milk.",
    "Don't put all your eggs in one basket.",
    "Every cloud has a silver lining.",
    "Fortune favors the bold.",
    "Haste makes waste.",
    "Hope for the best, prepare for the worst.",
    "If it ain't broke, don't fix it.",
    "If you can't beat 'em, join 'em.",
    "It takes two to tango.",
    "Keep your friends close and your enemies closer.",
    "Look before you leap.",
    "Make hay while the sun shines.",
    "Out of sight, out of mind.",
    "Practice makes perfect.",
    "Rome wasn't built in a day.",
    "The early bird catches the worm.",
    "The grass is always greener on the other side.",
    "The squeaky wheel gets the grease.",
    "Two wrongs don't make a right.",
    "When in Rome, do as the Romans do.",
    "You can't judge a book by its cover.",
    "You reap what you sow.",
    "Where there's smoke, there's fire."
]

start = int(round(time.time()) * 1000)
for text in proverbs:
    test_translate(text)
end = int(round(time.time()) * 1000)
print("translate benchmark: " + str(end - start) + "ms")


start = int(round(time.time()) * 1000)
for file_name in os.listdir("/opt/paddle_server_for_ai_env/benchmark/audio_to_vector"):
    test_audio("/opt/paddle_server_for_ai_env/benchmark/audio_to_vector/" + file_name)
end = int(round(time.time()) * 1000)
print("asr benchmark: " + str(end - start) + "ms")

print("\n")

start = int(round(time.time()) * 1000)
for file_name in os.listdir("/opt/paddle_server_for_ai_env/benchmark/test_images"):
    test_ocr("/opt/paddle_server_for_ai_env/benchmark/test_images/" + file_name)
end = int(round(time.time()) * 1000)
print("ocr benchmark: " + str(end - start) + "ms")

print("\n")

start = int(round(time.time()) * 1000)
for file_name in os.listdir("/opt/paddle_server_for_ai_env/benchmark/audio_to_vector"):
    test_vector("/opt/paddle_server_for_ai_env/benchmark/audio_to_vector/" + file_name)
end = int(round(time.time()) * 1000)
print("vector benchmark: " + str(end - start) + "ms")
