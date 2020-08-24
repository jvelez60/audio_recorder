# audio_recorder
Audio recording utility in python, designed to run on Raspberry pi 4 model B+.

HW adaptation:
  The program will acquire audio from the default card registered in Alsa utility:
1) install pyaudio 
2) run lsusb --> Show the existing USB devices
3) Run aplay -l --> displays the audio devices registered in the Raspberry.
4) Define the default audio card: edit /usr/share/alsa/alsa.conf and set:
      default.ctl.card = x (x= 1,2,3,...)
               default.pcm.card = x
5) If necessary, adjust in/out audio levels with alsamixer utility

- When GPIO-2 (button to ground) is pressed, interrupt callback_button_pressed is invoked
- LED attached to GPIO-3 is set to on (recording) or off (not recording)

                       GND               GPIO2: push button to GND
        o      o       o       o        GPIO3: resistor 220 ohm in series with LED to GND
        o      o       o       o
               GPIO2   GPIO3

August 23, 2020:

-------
I faced the following problem when trying to configure the program to run at boot time:
The program will crash when you initiate the USB sound card with a sampling rate different than 14400.
(error 9997 Invalid sample rte issued by pyaudio library)

This problem persisted with all possible variants when launching ut as a service in systemd or using crontab -e.
Finally managed to launch the program with any desired sampling rate by creating a audio_recorder.desktop file in
directory /etc/xdg/autostart with the followinf content:

[Desktop Entry]
Exec=python3 /home/pi/sw_dev/audio_recorder/audio_recorder.py
.





