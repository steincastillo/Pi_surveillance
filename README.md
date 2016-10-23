# Pi_surveillance
##Raspberry Pi home surveillance system

#####Overview
**Pi Surveillance** is a rich-function home surveillance system implemented on a raspberry pi. Main features inclue:  
* Permanent video monitoring  
* Motion detection  
* Enviroment sensing (with optional sense-hat)  
* Record monitor activity to a log file  
* Send email messages containing motion alarms (with pictures), system status, etc  
* Ability to control the monitor remotely over email  
* Fully configurable

#####What do you need
In order to properly run the Pi_surveillance system you will need:  
* Raspberry pi (B+ or higher) running and updated version of raspbian (PIXEL)  
* OpenCV properly configured   
* Pi Camera  
* Sense-hat (optional)  

#####DEFAULT.JSON file
Clone this repo and edit the conf.json file as follows:  
`send email:` [true/false] - set to 'true' if you want to receive an email with motion is detected  
`keep log:` [true/false] - set to 'true' if you want to save the activity on a log file  
`ghost video:` [true/false] - set to true if you want to see the motion detection video feed  
`echo`: [true/false] - set to true if your raspberry is connected to a screen  
`sys_check_seconds`: [number] of seconds to wait to check if a remote comand has been sent via email typically: 600  
`sense_hat`: [true/false] -  set to 'true' if you have a sense-hat attached and want to get temperature/pressure/humidity readings  
`camera_warmup_time`: [number] of seconds the camera needs to adjust focus, exposure, etc.  
`camera_resolution`: [number, number] to set the picture resolution  
`camera_fps`: [number] of frames per second. typically: 16  
`delta_thresh`: [number] to set the image threshold adjustment  
`min_area`: [number] of pixels that have to change in the image to sense motion  
`min_upload_seconds´: [number] of seconds to wait before consecutive uploads  
`min_motion_frames´: [number] of consecutive frames with motion required to trigger the alarm  
`fromaddr`: [email address] of your raspberry pi (sender) - Gmail account only!  
`smtpass` : [password] to your raspberry Gmail account  
`toaddr`: [email address] to whom the alarms and other information will be sent to  
`window_title` [title] of the video feed window  

several version of the **default.json** file can be saved for different situations

#####how to launch
Once you have configure the conf.json file to your needs launch the surveillance system from the command line:

##python3 pi_surveillance.py --conf default.json

#####Additional credits
This project was put together largely using the previous work of **Adrian Rosebrock** of [pyimagesearch] (http://www.pyimagesearch.com)
