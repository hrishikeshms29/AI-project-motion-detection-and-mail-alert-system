import os
import time
import glob
import numpy
import cv2
from emailing import send_email
from threading import Thread
import streamlit as st

video = cv2.VideoCapture(1)

# check1, frame1 = video.read()
# time.sleep(1)
#
# check2, frame2 = video.read()
# time.sleep(1)
#
# check3, frame3 = video.read()
# print(check3)
# print(frame3)
time.sleep(1)
check, frame = video.read()
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)
first_frame = gray_frame_gau
status_list = []
count = 1

def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)

clean_thread = Thread(target=clean_folder)
clean_thread.daemon = True
while True:
    status = 0
    check, frame = video.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    thresh_frame = cv2.threshold(delta_frame, 75, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=1)
    cv2.imshow("My video", dil_frame)

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images)/2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(target=send_email, args=(image_with_object, ))
        email_thread.daemon = True
        email_thread.start()

    print(status_list)

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

clean_thread.start()
video.release()
