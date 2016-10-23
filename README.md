# Pi_surveillance
##Raspberry Pi home surveillance system

#####Overview
**Pi Surveillance** is a rich-function home surveillance system implemented on a raspberry pi. Main features inclue:  
*Permanent video monitoring  
*Motion detection  
*Enviroment sensing (with optional sense-hat)  
*Record monitor activity to a log file  
*Send email messages containing motion alarms (with pictures), system status, etc  
*Ability to control the monitor remotely over email  
*Fully configurable

#####What do you need
In order to properly run the Pi_surveillance system you will need:  
*Raspberry pi (B+ or higher) running and updated version of raspbian (PIXEL)  
*OpenCV properly configured   
*Pi Camera  
*Sense-hat (optional)  

#####CONF.JSON file
Clone this repo and edit the conf.json file as follows:  
`send email:` [true/false] - set to 'true' if you want to receive an email with motion is detected  
`keep log:` [true/false] - set to 'true' if you want to save the activity on a log file  
`ghost video:` [true/false] - set to true if you want to see the motion detection video feed  
'echo': [true/false] - set to true if your raspberry is connected to a screen  
'sys_check_seconds': [number] of seconds to wait to check if a remote comand has been sent via email typicall: 600  
'sense_hat': [true/false] -  set to 'true' if you have a sense-hat attached and want to get temperature/pressure/humidity readings  


