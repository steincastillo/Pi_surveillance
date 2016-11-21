#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pi_surveillance.py
Date created: 08-Oct-2016
Version: 2.5
Author: Stein Castillo
Copyright 2016 Stein Castillo <stein_castillo@yahoo.com>  

USAGE: python3 pi_surveillance.py --conf [file.json]
"""

#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

#############
#    Libraries     #
#############

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
from datetime import timedelta
import argparse
import warnings
import datetime
import logging
import imutils
import json
import time
import cv2 as cv

import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#############
#    Functions   #
#############

#send_mail sends and email and attaches a file when required
def send_email(subj="Motion Detected!", filename="detection.jpg", body="Motion detected!!! @"):
    #prepare the email
    msg = MIMEMultipart()
    msg["From"]=FROMADDR
    msg["To"]=TOADDR
    msg["Subject"]=subj
    
    t_stamp = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    body = body +" "+ t_stamp
    msg.attach(MIMEText(body, "plain"))
    
    #attach the file
    if filename != None:
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

# log_setup create the logging file and adds the column titles
def log_setup(filename):
    logger.setLevel(logging.INFO)
    log_file = logging.FileHandler(filename, mode="w")
    log_format = logging.Formatter("%(asctime)s,[%(levelname)s],%(message)s", "%Y-%m-%d,%H:%M:%S")
    log_file.setFormatter(log_format)
    logger.addHandler(log_file)

# msg_out prints a formated message to the console    
def msg_out(typ = "I", msg = "null"):
    msg_time = datetime.datetime.now().strftime("%I:%M:%S%p")
    
    if typ == "I": mtype = "[INFO - "
    elif typ == "W": mtype = "[WARNING - "
    elif typ == "A": mtype = "[ALARM - "
    elif typ == "E": mtype = "[ERROR - "
    elif typ == "C": mtype = "[CMD - "
    else: mtype = "[UNKNOWN - "
        
    if conf["echo"]: print (mtype + msg_time + "] " + msg)
 
# sys_check scan the system mailbox for remote commands
def sys_check():
    cmd = "NC"
    try:
        mbox = imaplib.IMAP4_SSL("imap.gmail.com", 993) #Mail box reader
        result = mbox.login(FROMADDR, SMTPPASS)
        mbox.select()
        
        emfilter= "(FROM \"{}\")".format(TOADDR)
        result, data = mbox.uid("search", None,emfilter)
        latest = data[0].split()[-1]
       
        result, data = mbox.uid("fetch", latest, "(RFC822)")
        raw_msg = data[0][1]
        
        emsg = email.message_from_bytes(raw_msg)
        
        mbox.uid("STORE", latest, "+FLAGS", "(\Deleted)")
        mbox.expunge()
        
        #Analyze command
        if emsg["subject"]=="send picture": cmd = "C1"
        elif emsg["subject"]=="send log": cmd =  "C2"
        elif emsg["subject"]=="reset log": cmd = "C3"
        elif emsg["subject"]=="send system": cmd = "C4"
        elif emsg["subject"]=="send ping": cmd = "C5"
        elif emsg["subject"]=="stop email": cmd = "C6"
        elif emsg["subject"]=="start email": cmd = "C7"
        elif emsg["subject"]=="flash on": cmd = "C8"
        elif emsg["subject"]=="flash off": cmd = "C9"
        else: cmd = "UC"   
    except:
        cmd = "NC"
    finally:
        try:
            mbox.close()
            mbox.logout()
        finally:
            return cmd

# get_cpu_time obtains the system uptime by reading/parsing the /proc/uptime file
def  get_cpu_uptime():
    uptime = ""
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime = str(timedelta(seconds = uptime_seconds))
    return uptime
    
# get_cpu_load obtains the processor load by reading/parsing /proc/loadavg
def get_cpu_load():
    cpuload= open("/proc/loadavg","r").readline().split(" ")[:3]
    return cpuload 

# get_memory obtains the system available memory by reading/parsing the /proc/meminfo file    
def get_memory():
    meminfo = dict((i.split()[0].rstrip(":"), int(i.split()[1])) for i in open ("/proc/meminfo").readlines())
    return meminfo["MemAvailable"]
    
    
#######################
#  SENSE HAT Functions  #
#######################

#This function reads the cpu temperature    
def cpu_temp():
    tx = os.popen('/opt/vc/bin/vcgencmd measure_temp')
    cputemp = tx.read()
    cputemp = cputemp.replace('temp=','')
    cputemp = cputemp.replace('\'C\n','')
    cputemp = float(cputemp)
    return cputemp

#This function reads the SenseHat sensors    
def get_sense_data():

    sense_data = []
    cpu = cpu_temp()

    #Log "real" temperature corrected for CPU heat effect
    temp1 = sense.get_temperature()
    temp2 = sense.get_temperature_from_pressure()
    temp3 = sense.get_temperature_from_humidity()
    temp = ((temp1+temp2+temp3)/3)-(cpu/5)
    temp = round(temp,1)     
    sense_data.append(temp)  

    #Log humidity
    sense_data.append(round(sense.get_humidity(),1))

    #Log atmospheric pressure
    sense_data.append(round(sense.get_pressure(),1))
        
    return sense_data

#Display intermitent blue and red lights on the sense hat display    
def display_alarm (seconds = 5):
    time_in = datetime.datetime.now()
    while (datetime.datetime.now() - time_in).seconds <= seconds:
        sense.set_pixels(red_flag)
        time.sleep(0.3)
        sense.set_pixels(blue_flag)
        time.sleep(0.3)
    global sense_alarm
    #reset the sense hat alarm indicator and clear the display
    sense_alarm = False
    sense.clear()

def sense_flash(on = False):
    if on:
        sense.set_pixels(white_flag)
    else:
        sense.clear()
    

################
# Settings         #
################

#construct the command line argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
    help="usage: python3 pi_surveillance.py --conf [file.json]")
args = vars(ap.parse_args())
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

#emailing parameters settings
FROMADDR = conf["fromaddr"]  #email account
SMTPPASS = conf["smtppass"]  #email password
TOADDR = conf["toaddr"]      #email recipient

#log file settings
LOGNAME = "Pi_surveillance_"+datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")+".log"

#############
# Initialize     #
#############

#initialize console
if conf["echo"]:
    print("\n")
    print("**************************************")
    print("*          PI Surveillance           *")
    print("*                                    *")
    print("*           Version: 2.5             *")
    print("**************************************")
    print("\n")
    print ("[INFO] Press [q] to quit")
    print ("[INFO] Press [c] to capture image") 
    print("\n")
    print("Surveillance settings:")
    print("**********************")
    print ("  * Video feed: " + str(conf["show_video"]))
    print ("  * Delta Video: " + str(conf["ghost_video"]))
    print ("  * eMail: " + str(conf["send_email"]))
    print ("  * log file: " + str(conf["keep_log"]))
    print("**********************")
    print ("  * Resolution: " + str(conf["camera_resolution"]))
    print ("  * FPS : " + str(conf["camera_fps"]))
    print ("  * Sensibility: " + str(conf["min_motion_frames"]))
    print ("  * Min. Area: " + str(conf["min_area"]))
    print ("  * Rotation: " + str(conf["camera_rotation"]))
    print("**********************")
    print ("  * Sys Check: " + str(conf["sys_check_seconds"]))
    print ("  * Echo: " + str(conf["echo"]))
    print ("  * Sense Hat: " + str(conf["sense_hat"]))
    print ("  * Sense alarm: " + str(conf["alarm"]))
    print ("\n")

#Initialize LOG FILE
if conf["keep_log"]:
    logger = logging.getLogger("Pi_surveillance")
    log_setup(LOGNAME)
    msg_out("I", "Log file created...")
    logger.info("Log file created")

#initialize the SENSE HAT
sense_flag = False
if conf["sense_hat"]:
    from sense_hat import SenseHat #uncomment to use attached sense hat
    #from sense_emu import SenseHat #uncomment to use sense hat simulator
    import os
    try:
        sense=SenseHat()
        msg_out("I", "Sense Hat detected...")
        sense_flag = True
        sense_alarm = False
        
        #define sensor hat display colors
        R = [255, 0, 0]     #red
        B = [0, 0, 255]     #blue
        W = [255, 255, 255] #white
        E = [0, 0, 0]       #empty/black
        
        blue_flag = [
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B,
        B,B,B,B,B,B,B,B]
        
        red_flag = [
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R,
        R,R,R,R,R,R,R,R]
        
        white_flag = [
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W,
        W,W,W,W,W,W,W,W]

        if conf["keep_log"]: logger.info("Sense Hat detected...")
        sense.show_message("Sensing: ON", scroll_speed=0.05)
    except:
        msg_out("E", "Sense Hat NOT detected...")
        if conf["keep_log"]: logger.error("Sense hat NOT detected...")

#initialize CAMERA
msg_out("I", "Initializing camera...")
if conf["keep_log"]: logger.info("Initializing camera...")
avg = None
lastUploaded = datetime.datetime.now()
lastsyscheck = datetime.datetime.now()
motionCounter = 0 
camera = PiCamera()
camera.rotation = conf["camera_rotation"]
camera.resolution = tuple(conf["camera_resolution"])
camera.framerate = conf["camera_fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["camera_resolution"]))
time.sleep(conf["camera_warmup_time"])

#if required, create windows for live video feed
#else, display a static image with the background for reference
if conf["show_video"]:
    cv.namedWindow(conf["window_title"], cv.WINDOW_NORMAL)
else:
    img_static = PiRGBArray(camera)
    cv.namedWindow("STATIC IMAGE", cv.WINDOW_NORMAL)
    camera.capture(img_static, format="bgr")
    f_static = img_static.array
    cv.imshow("STATIC IMAGE", f_static)
    msg_out("I", "Static image initiated")
    if conf["keep_log"]: logger.info("Static image initiated...")

#if required, display delta and thresholded video    
if conf["ghost_video"]:
    cv.namedWindow("Thresh", cv.WINDOW_NORMAL)
    cv.namedWindow("Frame Delta", cv.WINDOW_NORMAL)

#############
#   Main loop   #
#############

#Initiate video capture from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #grab the raw NumPy array representing the image and initialize
    #the timestamp and occupied/unoccupied text
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Empty"
    
    #resize the frame, convert it to grayscal and blur it    
    #frame = imutils.resize(frame, width=500)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (21, 21), 0)
    
    #if the average frame is None, initialize it
    if avg is None:
        msg_out("I", "Starting background model...")
        if conf["keep_log"]: logger.info("Starting background model...")
        avg = gray.copy().astype("float")
        #Check image brightness
        means = cv.mean(gray)
        msg_out("I","Average image brightness [0-255]: "+str(int(means[0])))
        if means[0]<50:
            msg_out("W", "Image is too dark...")
            if conf["keep_log"]: logger.warning("Image is too dark...")
        rawCapture.truncate(0)
        msg_out("I", "System initiated...")
        if conf["keep_log"]: logger.info("System initiated...")
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
    cv.putText(frame, "Status: {}".format(text), (10, 20),
        cv.FONT_HERSHEY_SIMPLEX, 0.5, t_color, t_thick)
    cv.putText(frame, ts, (10, frame.shape[0] - 10), cv.FONT_HERSHEY_SIMPLEX, 
        0.4, (0, 0, 255), 1)
    
    #Add enviroment information
    if sense_flag:
        sense_data = get_sense_data()
        info = str(sense_data[0]) #temperature
        cv.putText(frame, "Temperature: {}".format(info), (10, 40),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
        info = str(sense_data[1]) #Humidity
        cv.putText(frame, "Humidity: {}".format(info), (10, 60),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
        info = str(sense_data[2]) #Pressure
        cv.putText(frame, "Pressure: {}".format(info), (10, 80),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
    #check to see if the room is occupied
    if text == "Occupied":
        #check if enough time has passed between alarms
        if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
            #increment the motion counter
            motionCounter += 1
            
            #check if the number of frames within consistent motion is 
            #high enough
            if motionCounter >= conf["min_motion_frames"]:
                msg_out("A", "Motion detected!!!")
                if conf["keep_log"]: logger.critical("Motion detected!!!")
                
                #check if alarm should be displayed on the sense hat
                if (sense_flag) and (conf["alarm"]) and (not sense_alarm):
                    msg_out("I","Sense Alarm Activated")
                    sense_alarm = True
                    Thread(target = display_alarm).start()
                
                if conf["send_email"]:
                    #save the frame
                    msg_out("I", "Saving frame...")
                    cv.imwrite("detection.jpg", frame)
                    msg_out("I", "Sending email...")
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
        
    #validate if system check is required
    if conf["sys_check_seconds"]>0:
        if (timestamp - lastsyscheck).seconds >= conf["sys_check_seconds"]:
            msg_out("I", "System check...")
            if conf["keep_log"]: logger.info("System check")
            lastsyscheck = timestamp
            cmd = sys_check()
            
            if cmd == "C1":     #send picture
                msg_out("C", "Send picture command received!")
                if conf["keep_log"]: logger.warning("Send picture command received!")
                msg_out("I", "Saving frame...")
                cv.imwrite("request.jpg", frame)
                msg_out("I", "Sending picture...")
                send_email("Requested Image", "request.jpg", "Sending requested image @")

            elif cmd == "C2":  #send log
                msg_out("C", "Send log command received!")
                if conf["keep_log"]: 
                    logger.warning("Send log command received!")
                    msg_out("I", "Sending log...")
                    send_email("Requested log file", LOGNAME, "Sending requested activity log @")
                else: 
                    send_email("Requested log file", None, "Log keeping option off!")

            elif cmd == "C3":     #reset log
                msg_out("C", "Reset log command received!")
                if conf["keep_log"]:
                    msg_out("I", "Deleting old log file")
                    os.remove(LOGNAME)
                    LOGNAME = "Pi_surveillance_"+datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")+".log"
                    log_setup(LOGNAME)
                    msg_out("I", "Log file created...")
                    logger.warning("Log file reset")
                
            elif cmd == "C4":     #send system
                msg_out("C", "Send system command received!")
                if conf["keep_log"]: logger.warning("Send system command received!")
                cpu_load = get_cpu_load()
                cpu_uptime = get_cpu_uptime()
                mem_ava = get_memory()
                #prepare system information file
                f1 = open ("sysinfo.csv", "w")
                line ="Time"+","+"Parm"+","+"Value"+"\n"
                f1.write(line)
                time_s = datetime.datetime.now().strftime("%H:%M:%S")
                line = time_s+","+"uptime"+","+cpu_uptime+"\n"
                f1.write(line)
                line = time_s+","+"CPU Load [1]"+","+cpu_load[0]+"\n"
                f1.write(line)
                line = time_s+","+"CPU Load [5]"+","+cpu_load[1]+"\n"
                f1.write(line)
                line = time_s+","+"CPU Load [15]"+","+cpu_load[2]+"\n"
                f1.write(line)
                line = time_s+","+"Ava. Memory"+","+str(mem_ava)+"\n"
                f1.write(line)
                means = cv.mean(gray)
                line = time_s+","+"Image brightness level"+","+str(int(means[0]))+"\n"
                f1.write(line)
                f1.flush()
                f1.close
                #send the email
                msg_out("I", "Sending system info")
                send_email("Requested sys info", "sysinfo.csv", "Requested system information")

            elif cmd == "C5":     #send ping
                msg_out("C", "Send ping command received!")
                if conf["keep_log"]: logger.warning("Send ping command received!")
                send_email("Requested Ping", None, "System up and running! @")

            elif cmd =="C6":    #stop email
                msg_out("C", "Stop email command received!")
                if conf["keep_log"]:
                    logger.warning("Stop email command received!")
                    conf["send_email"] = False

            elif cmd =="C7":    #start email
                msg_out("C", "Start email command received!")
                if conf["keep_log"]:
                    logger.warning("Start email command received!")
                    conf["send_email"] = True
                    send_email("eMail started", None, "eMail system started")
                    
            elif cmd == "C8":     #flash on
                msg_out("C", "Flash on command received!")
                if conf["keep_log"]: logger.warning("Flash on command received!")
                sense_flash(True)
                
            elif cmd == "C9":     #flash off
                msg_out("C", "Flash off command received!")
                if conf["keep_log"]: logger.warning("Flash off command received!")
                sense_flash(False)
                
                
    key = cv.waitKey(1) & 0xFF
    
    #if the "c" is pressed, capture image
    if key == ord("c"):
        msg_out("C", "Capture image")
        if conf["keep_log"]: logger.warning("Capture image")
        means = cv.mean(gray)
        means = means[0]
        if means < 50: msg_out("I", "Image too dark, Brightness level: "+str(int(means)))
        cv.imwrite("capture.jpg", frame)
        
    #if the "q" key is pressed, break from the loop
    if key == ord("q"):
        break
            
    #clear stream in preparation for the next frame
    rawCapture.truncate(0)
            
#cleanup the camera and close any open windows
msg_out("I", "Terminated by the user...")
if conf["keep_log"]: logger.info("Terminated by the user...")

#log surveillance settings
if conf["keep_log"]:
    logger.info ("[SET] Video feed: "+str(conf["show_video"]))
    logger.info("[SET] Delta video: "+str(conf["ghost_video"]))
    logger.info ("[SET] eMail: "+str(conf["send_email"]))
    logger.info ("[SET] Log file: "+str(conf["keep_log"]))
    logger.info ("[SET] Resolution: "+str(conf["camera_resolution"]))
    logger.info ("[SET] FPS: "+str(conf["camera_fps"]))
    logger.info ("[SET] Sensibility: "+str(conf["min_motion_frames"]))
    logger.info ("[SET] Rotation: "+str(conf["camera_rotation"]))
    logger.info ("[SET] Sys check: "+str(conf["sys_check_seconds"]))
    logger.info ("[SET] Echo: "+str(conf["echo"]))
    logger.info ("[SET] Sense hat: "+str(conf["sense_hat"]))

camera.close()
cv.destroyAllWindows()
