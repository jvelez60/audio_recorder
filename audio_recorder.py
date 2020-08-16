# *******************************************************************************************
#                           audio_recorder.py
#   Test program:
#   - When GPIO-2 (button to ground) is pressed, interrupt callback_button_pressed is invoked
#   - LED attached to GPIO-3 is set to on/off
#
# *******************************************************************************************

import RPi.GPIO as GPIO
import pyaudio
from datetime import datetime
import wave
import signal

# ------------- pyaudio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
# ------------ GPIO parameters
GPIO_REC = 2               # GPIO 2 is the record button
GPIO_LED = 3               # GPIO 3 is the LED recordding indicator

# ------------ Timeout thresholds
INIT_TIMEOUT = 3600
IDLE_TIMEOUT = 1800

# --------- Global variables
pressed = False
recording = False
wf = None
p = None
timeout = False           # Init timeout as false


# ---------------------------------------
def main():
    global pressed
    global recording
    global wf
    global p

    init_gpio(GPIO_REC, GPIO_LED)                 # Initialize GPIO: port 2: rec button, port 3: LED rec. indicator
# -----
    signal.signal(signal.SIGALRM, timeout_handler)     # Create the timeout handler
    signal.alarm(INIT_TIMEOUT)                         # Arm the timeout with the initial value
# -----

    p = pyaudio.PyAudio()                                            # Instantiate pyaudio
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,     # Create audio stream
                    input=True, frames_per_buffer=CHUNK, start = False,    # Don't start the stream immediately
                    stream_callback=callback_audio())

    while not timeout:
        # button is pressed when pin is LOW
        if pressed is True:
            pressed = False
            if recording is False:
                wf = init_audio_file()          # create new audio file
                stream.start_stream()           # Start audio stream
                print("recording started")
                signal.alarm(0)                 # Disarm timeout signal
            else:
                stream.stop_stream()      # Stop the audio stream
                wf.close()
                wf = None
                print("recording stopped")
                signal.alarm(IDLE_TIMEOUT)  # Arm timeout signal
            recording = not recording
            GPIO.output(GPIO_LED, recording)
#
    stream.close()
    p.terminate()
    GPIO.cleanup()    # cleanup and exit
    print"Program exiting... "
    exit()


# ---------------------------------------
def callback_button(self):
    global pressed
    pressed = True
    return


# ---------------------------------------
def callback_audio():
    global wf

    def callback(in_data, frame_count, time_info, flag):
        wf.writeframes(in_data)
        return in_data, pyaudio.paContinue
    return callback


# ---------------------------------------
def init_audio_file():
    global FORMAT
    global p
    utc_datetime = datetime.utcnow()
    time_string = utc_datetime.strftime("%Y_%m_%d-%H.%M.%S-UTC")
    handler = wave.open(time_string + ".wav", 'wb')
    handler.setnchannels(CHANNELS)
    handler.setsampwidth(p.get_sample_size(FORMAT))
    handler.setframerate(RATE)
    return handler


# ---------------------------------------
def init_gpio(portin, portout):
    GPIO.setmode(GPIO.BCM)                                 # Broadcom pin-numbering scheme
    GPIO.setup(portin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button to GPIOx (portin)
    GPIO.setup(portout, GPIO.OUT)                          # LED to GPIOy (portout)
    GPIO.output(portout, False)                            # Init LED to off
    GPIO.add_event_detect(portin, GPIO.FALLING, bouncetime=200,      # Define button pressed callback
                          callback=callback_button)
    return


# ---------------------------------------
def timeout_handler(signum, frame):
    global timeout                                         # Timeout handler
    timeout = True
    print("Timeout")
    return

# #######################################################
# Execute `main()` function

if __name__ == '__main__':
    main()

#