#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  

"""
pi_surveillance.py
Date created: 08-Oct-2016
Version: 1.4
Author: Stein Castillo
Copyright 2016 Stein Castillo <stein_castillo@yahoo.com>  

USAGE: python3 pi_surveillance.py --conf [file.json]
"""

#############
# Libraries #
#############
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2 as cv

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#############
# Functions #
#############

#This function sends and email and a picture when motion is detected
def send_email(subj="Motion Detected!", filename="detection.jpg"):
    #prepare the email
    msg = MIMEMultipart()
    msg["From"]=FROMADDR
    msg["To"]=TOADDR
    msg["Subject"]=subj
    
    t_stamp = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    body = "Motion has been detected "+" at "+ t_stamp
    msg.attach(MIMEText(body, "plain"))
    attachment = open(filename, "rb")
    
    part = MIMEBase("application", "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment; filename= %s" % filename)
    
    msg.attach(part)
    
    #send the email    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(FROMADDR, SMTPPASS)
    text = msg.as_string()
    server.sendmail(FROMADDR, TOADDR, text)
    server.quit()

def log_setup(filename):
    header = []
    header.append("Type")
    header.append("Time")
    header.append("Message")
    
    with open(filename, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")

def write_log(m_type, message):
    time_s = datetime.datetime.now().strftime("%H:%M:%S")
    line = m_type+","+time_s+","+message+"\n"
    f = open (FILENAME, "a")
    f.write(line)
    f.flush()
    f.close
    
    
####################
#    Settings     #
####################

#construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
    help="usage: python3 pi_surveillance.py --conf [file.json]")
args = vars(ap.parse_args())
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

#camera settings
camera = PiCamera()
camera.rotation = conf["camera_rotation"]
camera.resolution = tuple(conf["camera_resolution"])
camera.framerate = conf["camera_fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["camera_resolution"]))

#emailing parameters settings
FROMADDR = conf["fromaddr"]  #email account
SMTPPASS = conf["smtppass"]  #email password
TOADDR = conf["toaddr"]      #email recipient

#log file settings
#FILENAME = "Pi_survelillance_"+datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")+".csv"
FILENAME ="test.csv"


#############
# Main loop #
#############

print("\n")
print("**************************************")
print("*          PI Surveillance           *")
print("*                                    *")
print("*           Version: 1.4             *")
print("**************************************")
print("\n")
print ("[INFO] Press [q] to quit")
print("\n")
print("Surveillance settings:")
print ("  * Resolution: " + str(conf["camera_resolution"]))
print ("  * FPS : " + str(conf["camera_fps"]))
print ("  * Sensibility: " + str(conf["min_motion_frames"]))
print ("  * Rotation: " + str(conf["camera_rotation"]))
print ("  * Video feed: " + str(conf["show_video"]))
print ("  * Delta Video: " + str(conf["ghost_video"]))
print ("  * eMail: " + str(conf["send_email"]))
print ("  * log file: " + str(conf["keep_log"]))
print ("\n")

if conf["keep_log"]:
    log_setup(FILENAME)

print ("[INFO - "+ datetime.datetime.now().strftime("%I:%M:%S%p")+"] Initializig camera... ")

if conf["keep_log"]: write_log("[INFO]", "Initializing camera...")
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0 
time.sleep(conf["camera_warmup_time"])

#if requeried, create windows for video feed
if conf["show_video"]:
    cv.namedWindow(conf["window_title"], cv.WINDOW_NORMAL)
if conf["ghost_video"]:
    cv.namedWindow("Thresh", cv.WINDOW_NORMAL)
    cv.namedWindow("Frame Delta", cv.WINDOW_NORMAL)

#Initiate video capture from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #grab the raw NumPy array representing the image and initialize
    #the timestamp and occupied/unoccupied text
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Empty"
    
    #resize the frame, convert it to grayscal and blur it    
    frame = imutils.resize(frame, width=500)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (21, 21), 0)
    
    #if the average frame is None, initialize it
    if avg is None:
        print ("[INFO - "+datetime.datetime.now().strftime("%I:%M:%S%p")+"] Starting background model... ")
        if conf["keep_log"]: write_log("[INFO]", "Starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        print ("[INFO - "+datetime.datetime.now().strftime("%I:%M:%S%p")+"] System initiated...")
        if conf["keep_log"]: write_log("[INFO]", "System initiated...")
        continue
        
    #accumulate the weighted average between the current frame and
    #previous frames, then compute the difference between the current
    #fram and running average
    
    cv.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv.absdiff(gray, cv.convertScaleAbs(avg))
    
    #threshold the delta image, dilate the thresholded image to fill in holes, then find countours
    #on thresholded image
    thresh = cv.threshold(frameDelta, 5, 255, cv.THRESH_BINARY)[1]
    thresh = cv.dilate(thresh, None, iterations=2)
    (_, cnts, _) = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
		cv.CHAIN_APPROX_SIMPLE)

    #loop over the contours
    for c in cnts:
        #if the contour is too small, ignore it
        if cv.contourArea(c) < conf["min_area"]:
            continue
        
        #compute the bounding box for the contour, draw it on the frame
        #and update the text
        (x, y, w, h) = cv.boundingRect(c)
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = "Occupied"
        
    #draw the text and timestamp the frame
    if text == "Empty":
        t_color = (0,255,0)     #green text
        t_thick = 1
    else:
        t_color = (0, 0, 255)   #red text
        t_thick = 2
        
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv.putText(frame, "Room status: {}".format(text), (10, 20),
        cv.FONT_HERSHEY_SIMPLEX, 0.5, t_color, t_thick)
    cv.putText(frame, ts, (10, frame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX, 
        0.4, (0, 0, 255), 1)
        
    #check to see if the room is occupied
    if text == "Occupied":
        #check if enough time has passed between alarms
        if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
            #increment the motion counter
            motionCounter += 1
            
            #check if the number of frames within consistent motion is 
            #high enough
            if motionCounter >= conf["min_motion_frames"]:
                print ("[ALARM - "+datetime.datetime.now().strftime("%I:%M:%S%p")+"] Motion detected!!!")
                if conf["keep_log"]: write_log("[ALARM]", "Motion detected!!!")
                
                if conf["send_email"]:
                    #save the frame
                    print ("[INFO] Saving frame...")
                    cv.imwrite("detection.jpg", frame)
                    print ("[INFO] Sending email...")
                    Thread(target=send_email).start()
                    
                #update last alarm timestamp and reset motion counter
                lastUploaded = timestamp
                motionCounter = 0
    #otherwise, the room is empty
    else:
        motionCounter = 0
            
    #display the security feed
    if conf["show_video"]:
        cv.imshow(conf["window_title"], frame)
    if conf["ghost_video"]:
        cv.imshow("Thresh", thresh)
        cv.imshow("Frame Delta", frameDelta)
        
    key = cv.waitKey(1) & 0xFF
        
    #if the "q" key is pressed, break from the loop
    if key == ord("q"):
        break
            
    #clear stream in preparation for the next frame
    rawCapture.truncate(0)
            
#cleanup the camera and close any open windows
print ("[INFO - "+datetime.datetime.now().strftime("%I:%M:%S%p")+"] Terminated by the user...")
if conf["keep_log"]: write_log("[INFO]", "Terminated by the user...")
camera.close()
cv.destroyAllWindows()


