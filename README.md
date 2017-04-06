# Pi_surveillance
## Raspberry Pi home surveillance system

### Overview
**Pi Surveillance** is a function rich home surveillance system implemented on a Raspberry Pi. Main features include:  
* Permanent video monitoring  
* Motion detection  
* Enviroment sensing (with optional sense-hat)  
* Record monitor activity to a log file  
* Send email messages containing motion alarms (with picture), system status, etc  
* Ability to control the monitor remotely over email  
* Access[OpenWeatherMap] (http://openweathermap.org)  for real time weather report  
* Code independent configuration  

### What you need
In order to properly run the Pi_surveillance system you will need:  
* Raspberry Pi (2 or higher) running and updated version of raspbian (PIXEL)  
* OpenCV properly configured   
* Pi Camera  
* Sense-hat (optional)  
* Internet connection (optional)  

### DEFAULT.JSON file
The .json configuration file controls the surveillance monitor behavior. Also, gives the user control over the monitoring parameters without the need of changing the code. 

The available configuration elements are:    
`send email:` [true/false] - set to 'true' if you want to receive an email when motion is detected  
`keep log:` [true/false] - set to 'true' if you want to save the activity on a log file  
`ghost video:` [true/false] - set to true if you want to see the motion detection video feed  
`echo`: [true/false] - set to true if your raspberry is connected to a screen  
`alarm`: [true/false] - display blinking blue/red lights on the sense hat display when motion is detected  
`oweather`: [true/false] - set to true if you wish to obtain the weather report from OpenWeatherMap  
`oweather_key`: [openweahter_key] - you can obtain this key for free at [OpenWeatherMap] (http://openweathermap.org)  
`oweather_city`: [openweahter_city_code] - City where you want to obtain the wheather report from  
`sys_check_seconds`: [number] of seconds to wait to check if a remote comand has been sent via email typically: 600  
`sense_hat`: [true/false] -  set to 'true' if sense-hat attached and want to get temperature/pressure/humidity readings  
`camera_warmup_time`: [number] of seconds the camera needs to adjust focus, exposure, etc.  
`camera_resolution`: [number, number] to set the picture resolution  
`camera_rotation`: [number] to set the camera rotation in degrees   
`camera_fps`: [number] of frames per second. typically: 16  
`delta_thresh`: [number] to set the image threshold adjustment  
`min_area`: [number] of pixels that have to change in the image to sense motion. Tipically: 2000  
`min_upload_seconds`: [number] of seconds to wait before consecutive uploads  
`min_motion_frames`: [number] of consecutive frames with motion required to trigger the alarm  
`fromaddr`: [email address] of your raspberry pi (sender) - Gmail account only!  
`smtpass` : [password] to your raspberry Gmail account  
`toaddr`: [email address] to whom the alarms and other information will be sent to  
`window_title` [title] of the video feed window  

several version of the **default.json** file can be saved to acommodate different needs  

### Installation
To install the Pi Surveillance monitor, simply copy the following files to the same directory:
* pi_surveillance.py  
* default.json  

### Remote control 
**Pi_surveillance** can be remotely controled. You just need to set a Gmail account for the raspberry. Commands to the monitor are sent using the subject line of the email.  
The available commands are:  
* **send picture**: Take a picture and send it back  
* **send ping**: Send a short text indicating the system is up and running  
* **send log**: Send the system log file  
* **send system**: Send file with current uptime, processor load, CPU temperature and other system parameters    
* **reset log**: Initialize the log file and erase the current file  
* **stop email**: Stops the monitor from sending emails when motion is detected  
* **start email**: Initiates the emails sending when motion is detected  
* **flash on**: Turns the sense hat display on (all white)  
* **flash off**: Turns the sense hat display off  
* **home**: Deactivates the keep log and send mail  
* **away**: Activates keep log and send mail  

### Usage
To launch the surveillance system from the command line:

#### python3 pi_surveillance.py --help
#### python3 pi_surveillance.py --conf default.json  

### Console commands
While running pi_surveillance from a terminal, you can use use the following commands:  
`a`: Set AWAY mode (activates email and log recording)  
`b`: Display the brightness level of the current video feed   
`c`: Capture current video feed to a still image  
`e`: Display Sense Hat environment sensors information and weather report  
`o`: Set HOME mode (disables email and log recording)  
`h`: Display terminal commands help  
`q`: Terminate the program  

### Additional credits
This project is based on previous work done by **Adrian Rosebrock** of [pyimagesearch] (http://www.pyimagesearch.com)

### Additional notes
Current version is **2.6**.  
This version of the monitor has been tested with Pyhton 3  and raspberry Pi 3 only.  
To ensure proper execution launch the application from the terminal command line (NOT IDLE).  
Please check license.txt for licensing terms.  
